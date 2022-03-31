import typing as t

from t4cclient.config import config


def get_username(token: t.Dict[str, t.Any]) -> str:
    return token[config["authentication"]["jwt"]["usernameClaim"]].strip()
