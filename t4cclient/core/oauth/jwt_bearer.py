import typing as t
import time
import requests

from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from pydantic import BaseModel
from t4cclient.config import OAUTH_CLIENT_ID, OAUTH_ENDPOINT
from t4cclient.core.database import SessionLocal, users


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)
        if not credentials or credentials.scheme != "Bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=401,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        token_decoded = self.validate_token(credentials.credentials)
        self.initialize_user(token_decoded)
        return token_decoded

    def initialize_user(self, token_decoded: t.Dict[str, str]):
        with SessionLocal() as session:
            users.find_or_create_user(session, token_decoded["sub"])

    def validate_token(self, token: str) -> t.Dict[str, t.Any]:
        key = KeyStore.key_for_token(token)
        try:
            return jwt.decode(
                token, key.dict(), audience=OAUTH_CLIENT_ID
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401,
                detail={
                    "err_code": "token_exp",
                    "reason": "The Signature of the token is expired. Please request a new access token.",
                },
            )
        except (jwt.JWTError, jwt.JWTClaimsError) as e:
            raise HTTPException(
                status_code=401,
                detail="The token verification failed. Please try again with another access token.",
            )


# Copied and adapted from https://github.com/marpaia/jwks/blob/master/jwks/jwks.py:

class _KeyStore:

    def __init__(
        self,
        *,
        jwks_uri: str,
        algorithms: t.List[str] = ["RS256"],
        key_refresh_interval=3600,
    ):
        self.jwks_uri = jwks_uri
        self.algorithms = algorithms
        self.public_keys = {}
        self.key_refresh_interval = key_refresh_interval
        self.refresh_keys()

    def keys_need_refresh(self) -> bool:
        return (time.time() - self.public_keys_last_refreshed) > self.key_refresh_interval

    def refresh_keys(self) -> None:
        resp = requests.get(self.jwks_uri)
        jwks = JSONWebKeySet.parse_raw(resp.text)
        self.public_keys_last_refreshed = time.time()
        self.public_keys.clear()
        for key in jwks.keys:
            self.public_keys[key.kid] = key

    def key_for_token(self, token: str, *, in_retry: int = 0) -> t.Dict[str, t.Any]:
        # Before we do anything, the validation keys may need to be refreshed.
        # If so, refresh them.
        if self.keys_need_refresh():
            self.refresh_keys()

        # Try to extract the claims from the token so that we can use the key ID
        # to determine which key we should use to validate the token.
        try:
            unverified_claims = jwt.get_unverified_header(token)
        except Exception:
            raise InvalidTokenError("Unable to parse key ID from token")

        # See if we have the key identified by this key ID.
        try:
            return self.public_keys[unverified_claims["kid"]]
        except KeyError:
            # If we don't have this key and this is the first attempt (ie: we
            # haven't refreshed keys yet), then try to refresh the keys and try
            # again.
            if in_retry:
                raise KeyIDNotFoundError()
            self.refresh_keys()
            return self.validate_token(token, in_retry=1)


def get_jwks_uri_for_azure_ad(authorization_endpoint=OAUTH_ENDPOINT):
    discoveryEndpoint = f"{authorization_endpoint}/v2.0/.well-known/openid-configuration"

    config = requests.get(discoveryEndpoint).json()
    return config["jwks_uri"]


class JSONWebKey(BaseModel):
    # alg: str
    kty: str
    use: str
    n: str
    e: str
    kid: str
    x5t: str
    x5c: t.List[str]


class JSONWebKeySet(BaseModel):
    keys: t.List[JSONWebKey]


class InvalidTokenError(Exception):
    pass


class KeyIDNotFoundError(Exception):
    pass


# Our "singleton" key store:
KeyStore = _KeyStore(jwks_uri=get_jwks_uri_for_azure_ad())
