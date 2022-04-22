import typing as t

import requests
from requests_oauthlib import OAuth2Session
from t4cclient.config import config

cfg = config["authentication"]["oauth"]


auth_args = {}
if cfg["scopes"]:
    auth_args["scopes"] = cfg["scopes"]
auth_session = OAuth2Session(
    cfg["client"]["id"], redirect_uri=cfg["redirectURI"], **auth_args
)


def get_auth_redirect_url() -> t.Dict[str, str]:
    auth_url, state = auth_session.authorization_url(
        read_well_known()["authorization_endpoint"],
        grant_type="authorization_code",
    )
    return {"auth_url": auth_url, "state": state}


def get_token(code: str) -> t.Dict[str, t.Any]:
    return auth_session.fetch_token(
        read_well_known()["token_endpoint"],
        code=code,
        client_id=cfg["client"]["id"],
        client_secret=cfg["client"]["secret"],
    )


def refresh_token(refresh_token: str) -> t.Dict[str, t.Any]:
    return auth_session.refresh_token(
        read_well_known()["token_endpoint"],
        refresh_token=refresh_token,
        client_id=cfg["client"]["id"],
        client_secret=cfg["client"]["secret"],
    )


def read_well_known() -> dict[str, t.Any]:
    if cfg["endpoints"]["wellKnown"]:
        r = requests.get(
            cfg["endpoints"]["wellKnown"], timeout=config["requests"]["timeout"]
        )
        r.raise_for_status()

        resp = r.json()

        authorization_endpoint = resp["authorization_endpoint"]
        token_endpoint = resp["token_endpoint"]
    else:
        authorization_endpoint = cfg["endpoints"]["authorization"]
        token_endpoint = cfg["endpoints"]["tokenIssuance"]

    return {
        "authorization_endpoint": authorization_endpoint,
        "token_endpoint": token_endpoint,
    }
