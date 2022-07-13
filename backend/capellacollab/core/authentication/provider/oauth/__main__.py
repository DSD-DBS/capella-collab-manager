from capellacollab.config import config

import typing as t
from .keystore import KeyStore

cfg = config["authentication"]["oauth"]


def get_jwk_cfg(token: str) -> t.Dict[str, any]:
    return {
        "algorithms": ["RS256"],
        "audience": cfg["audience"] or cfg["client"]["id"],
        "key": KeyStore.key_for_token(token).dict(),
    }
