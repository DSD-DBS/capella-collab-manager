import typing as t

from requests_oauthlib import OAuth2Session
from t4cclient.config import (OAUTH_CLIENT_ID, OAUTH_CLIENT_SECRET,
                              OAUTH_ENDPOINT, OAUTH_REDIRECT_URI,
                              OAUTH_TOKEN_ENDPOINT)

auth_session = OAuth2Session(OAUTH_CLIENT_ID, redirect_uri=OAUTH_REDIRECT_URI)


def get_auth_redirect_url() -> t.Dict[str, str]:
    auth_url, state = auth_session.authorization_url(
        OAUTH_ENDPOINT + "/authorize", grant_type="authorization_code"
    )
    return {"auth_url": auth_url, "state": state}


def get_token(code: str) -> t.Dict[str, t.Any]:
    return auth_session.fetch_token(
        OAUTH_TOKEN_ENDPOINT,
        code=code,
        client_id=OAUTH_CLIENT_ID,
        client_secret=OAUTH_CLIENT_SECRET,
    )

def refresh_token(refresh_token: str) -> t.Dict[str, t.Any]:
    return auth_session.refresh_token(
        OAUTH_TOKEN_ENDPOINT,
        refresh_token=refresh_token,
        client_id=OAUTH_CLIENT_ID,
        client_secret=OAUTH_CLIENT_SECRET,
    )
