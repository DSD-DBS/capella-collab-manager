# Standard library:
import typing as t
from __future__ import annotations

# local:
from .keystore import KeyStore
from t4cclient.config import config

cfg = config["authentication"]["oauth"]


def get_jwk_cfg(token: str) -> dict[str, t.Any]:
    return {
        "algorithms": ["RS256"],
        "audience": cfg["audience"] or cfg["client"]["id"],
        "key": KeyStore.key_for_token(token).dict(),
    }
