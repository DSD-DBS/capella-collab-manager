# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

# Standard library:
import logging
import re
import typing as t

# 3rd party:
import requests

# local:
from t4cclient import config
from t4cclient.core.operators import OPERATOR
from t4cclient.schemas.sessions import WorkspaceType
from t4cclient.sessions.models import DatabaseSession

log = logging.getLogger(__name__)


def inject_attrs_in_sessions(
    db_sessions: t.List[DatabaseSession],
) -> t.List[t.Dict[str, t.Any]]:
    sessions_list = []
    for session in db_sessions:
        session_dict = session.__dict__
        session_dict["state"] = _determine_session_state(session_dict)
        session_dict["last_seen"] = get_last_seen(session.id)
        session_dict["owner"] = session_dict["owner_name"]

        sessions_list.append(session_dict)

    return sessions_list


def get_last_seen(sid: str) -> str:
    """Return project session last seen activity"""
    url = config.config["prometheus"]["url"]
    url += "/".join(("api", "v1", "query?query=idletime_minutes"))
    try:
        response = requests.get(url)
        for session in response.json()["data"]["result"]:
            if sid == session["metric"]["app"]:
                return _get_last_seen(float(session["value"][1]))
        log.exception("No session was found.")
        return "UNKNOWN"
    except requests.ConnectionError as error:
        log.exception("ConnectionError: %s", error.args[0])
        return "UNKNOWN"
    except KeyError:
        log.exception("Something is wrong with prometheus idletime metric.")
        return "UNKNOWN"


def _get_last_seen(idletime: int | float) -> str:
    if idletime == -1:
        return "Never connected"

    if (idlehours := idletime / 60) > 1:
        return f"{round(idlehours, 2)} hrs ago"

    return f"{idletime} mins ago"


def _determine_session_state(session: t.Dict[str, t.Any]) -> str:
    state = OPERATOR.get_session_state(session["id"])

    if session["type"] == WorkspaceType.READONLY:
        try:
            if state == "Started" or state == "BackOff":
                logs = OPERATOR.get_session_logs(session["id"]).splitlines()
                for line in logs:
                    res = re.search(r"^---(.*?)---$", line)
                    if res:
                        state = res.group(1)
        except:
            log.exception("Could not parse log")
    return state
