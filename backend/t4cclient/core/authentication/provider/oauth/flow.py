import typing as t

from requests_oauthlib import OAuth2Session
from t4cclient.config import config

cfg = config["authentication"]["oauth"]

auth_session = OAuth2Session(
    cfg["client"]["id"], redirect_uri=cfg["redirectURI"], scope="openid"
)


def get_auth_redirect_url() -> t.Dict[str, str]:
    auth_url, state = auth_session.authorization_url(
        cfg["endpoints"]["authorization"],
        grant_type="authorization_code",
    )
    return {"auth_url": auth_url, "state": state}


def get_token(code: str) -> t.Dict[str, t.Any]:
    return auth_session.fetch_token(
        cfg["endpoints"]["tokenIssuance"],
        code=code,
        client_id=cfg["client"]["id"],
        client_secret=cfg["client"]["secret"],
    )


def refresh_token(refresh_token: str) -> t.Dict[str, t.Any]:
    return auth_session.refresh_token(
        cfg["endpoints"]["tokenIssuance"],
        refresh_token=refresh_token,
        client_id=cfg["client"]["id"],
        client_secret=cfg["client"]["secret"],
    )
