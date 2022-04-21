# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

from requests_oauthlib import OAuth2Session
from t4cclient.config import (
    OAUTH_CLIENT_ID,
    OAUTH_CLIENT_SECRET,
    OAUTH_ENDPOINT,
    OAUTH_REDIRECT_URI,
    OAUTH_TOKEN_ENDPOINT,
)

auth_session = OAuth2Session(OAUTH_CLIENT_ID, redirect_uri=OAUTH_REDIRECT_URI)


def get_auth_redirect_url(state) -> t.Dict[str, str]:
    auth_url, state = auth_session.authorization_url(
        OAUTH_ENDPOINT + "/authorize", state=state, grant_type="authorization_code"
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

class OAuthStub:
    def initiate_auth_code_flow(self, scopes, state):
        return get_auth_redirect_url(state)

    def acquire_token_by_auth_code_flow(self, auth_data, body, scopes=[]):
        get_token(body.code)

    def acquire_token_by_refresh_token(self, body, scopes=[]):
        ...

    def get_accounts(self):
        return []
    
    def remove_account(self, account):
        ...
