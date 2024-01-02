# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import re
from collections import abc

import requests

from capellacollab.config import config

from . import models, operators

log = logging.getLogger(__name__)


def inject_attrs_in_sessions(
    db_sessions: abc.Sequence[models.DatabaseSession],
) -> list[models.GetSessionsResponse]:
    sessions_list = []
    for session in db_sessions:
        session_dict = models.Session.model_validate(session).model_dump()

        session_dict["state"] = _determine_session_state(session)
        session_dict["last_seen"] = get_last_seen(session.id)

        if session.environment:
            session_dict["jupyter_uri"] = session.environment.get(
                "JUPYTER_URI"
            )
            session_dict["t4c_password"] = session.environment.get(
                "T4C_PASSWORD"
            )

        sessions_list.append(
            models.GetSessionsResponse.model_validate(session_dict)
        )

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
    except requests.JSONDecodeError as error:
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

    return f"{idletime:.0f} mins ago"


def _determine_session_state(session: models.DatabaseSession) -> str:
    state = operators.get_operator().get_session_state(session.id)

    if state in ("Started", "BackOff"):
        try:
            logs = operators.get_operator().get_session_logs(session.id)
            res = re.search(r"(?s:.*)^---(.*?)---$", logs, re.MULTILINE)
            if res:
                return res.group(1)
        except Exception:
            log.exception("Could not parse log")
    return state
