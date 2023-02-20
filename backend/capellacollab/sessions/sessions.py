# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import logging
import re
import typing as t

import requests
from requests import JSONDecodeError

from capellacollab.config import config
from capellacollab.sessions.models import DatabaseSession
from capellacollab.sessions.operators import get_operator
from capellacollab.sessions.schema import WorkspaceType

log = logging.getLogger(__name__)


def inject_attrs_in_sessions(
    db_sessions: list[DatabaseSession],
) -> list[dict[str, t.Any]]:
    sessions_list = []
    for session in db_sessions:
        session.state = _determine_session_state(session)
        session.last_seen = get_last_seen(session.id)
        session.session_domain = get_operator().session_domain
        sessions_list.append(session)

    return sessions_list


def get_last_seen(sid: str) -> str:
    """Return project session last seen activity"""
    url = config["prometheus"]["url"]
    url += "/".join(("api", "v1", "query?query=idletime_minutes"))
    try:
        response = requests.get(
            url,
            timeout=config["requests"]["timeout"],
        )
        response.raise_for_status()
        for session in response.json()["data"]["result"]:
            if sid == session["metric"]["app"]:
                return _get_last_seen(float(session["value"][1]))
        log.exception("No session was found.")
    except JSONDecodeError as error:
        log.exception("Prometheus service not available: %s", error.args[0])
    except requests.ConnectionError as error:
        log.exception("ConnectionError: %s", error.args[0])
    except KeyError:
        log.exception("Something is wrong with prometheus idletime metric.")
    except Exception:
        log.exception("Exception during fetching of last seen.")
    return "UNKNOWN"


def _get_last_seen(idletime: int | float) -> str:
    if idletime == -1:
        return "Never connected"

    if (idlehours := idletime / 60) > 1:
        return f"{round(idlehours, 2)} hrs ago"

    return f"{idletime} mins ago"


def _determine_session_state(session: DatabaseSession) -> str:
    state = get_operator().get_session_state(session.id)

    if session.type == WorkspaceType.READONLY:
        try:
            if state in ("Started", "BackOff"):
                logs = get_operator().get_session_logs(session.id).splitlines()
                for line in logs:
                    res = re.search(r"^---(.*?)---$", line)
                    if res:
                        state = res.group(1)
        except Exception:
            log.exception("Could not parse log")
    return state
