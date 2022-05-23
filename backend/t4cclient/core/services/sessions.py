# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import logging
import re
import requests
import typing as t

from t4cclient import config
from t4cclient.core.operators import OPERATOR
from t4cclient.schemas.sessions import WorkspaceType
from t4cclient.sql_models.sessions import DatabaseSession

log = logging.getLogger(__name__)


def inject_attrs_in_sessions(
    db_sessions: t.List[DatabaseSession],
) -> t.List[t.Dict[str, t.Any]]:
    sessions_list = []
    for s in db_sessions:
        session_dict = s.__dict__
        session_dict["state"] = _determine_session_state(session_dict)
        session_dict["last_seen"] = get_last_seen(db_sessions.id)
        session_dict["owner"] = session_dict["owner_name"]

        sessions_list.append(session_dict)

    return sessions_list


def get_last_seen(id: str) -> str:
    """Return project session last seen activity"""
    r = requests.get(config["prometheus"]["externalUrl"])
    result = r.json()["result"][int(id)]
    return _get_last_seen(result)


def _get_last_seen(idletime: int | float) -> str:
    if idletime == -1:
        "Never connected"
    last_seen = datetime.now() - datetime.timedelta(minutes=idletime)
    time = last_seen.strftime("%m/%d/%Y %H:%M:%S")
    return f"{idletime}mins ago ({time})"


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
