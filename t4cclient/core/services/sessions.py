import typing as t

import t4cclient.extensions.t4c as t4c_manager
from t4cclient import config
from t4cclient.core.operators import OPERATOR
from t4cclient.sql_models.sessions import DatabaseSession


def inject_attrs_in_sessions(
    db_sessions: t.List[DatabaseSession],
) -> t.List[t.Dict[str, t.Any]]:
    sessions_list = []
    for s in db_sessions:
        session_dict = s.__dict__
        session_dict["state"] = OPERATOR.get_session_state(session_dict["id"])
        session_dict["last_seen"] = t4c_manager.fetch_last_seen(session_dict["mac"])
        session_dict["owner"] = session_dict["owner_name"]

        sessions_list.append(session_dict)

    return sessions_list
