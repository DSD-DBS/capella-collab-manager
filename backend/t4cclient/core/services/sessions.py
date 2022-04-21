# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import re
import typing as t

import t4cclient.extensions.modelsources.t4c.connection as t4c_manager
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
        session_dict["last_seen"] = t4c_manager.fetch_last_seen(session_dict["mac"])
        session_dict["owner"] = session_dict["owner_name"]

        sessions_list.append(session_dict)

    return sessions_list


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
