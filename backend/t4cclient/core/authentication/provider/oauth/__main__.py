from t4cclient.config import config

cfg = config["authentication"]["oauth"]


def get_jwk_cfg(token: str) -> dict[str, any]:
    return {
        "algorithms": ["RS256"],
        "audience": cfg["client"]["id"],
        "key": cfg["publicKey"],
    }
