import typing as t

from t4cclient import config


def get_username(token: t.Dict[str, t.Any]) -> str: 
    return token[config.USERNAME_CLAIM].strip()
