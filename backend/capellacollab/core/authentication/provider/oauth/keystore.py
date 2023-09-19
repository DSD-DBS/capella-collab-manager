# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

# pylint: skip-file


import logging
import time
import typing as t

import jwt
import requests

from capellacollab.config import config
from capellacollab.core.authentication.provider import models

from .. import models as provider_models

log = logging.getLogger(__name__)
cfg = config["authentication"]["oauth"]


# Copied and adapted from https://github.com/marpaia/jwks/blob/master/jwks/jwks.py:


class _KeyStore:
    def __init__(
        self,
        *,
        get_jwks_uri: t.Callable[[], str],
        algorithms: list[str] | None = None,
        key_refresh_interval=3600,
    ):
        if not algorithms:
            algorithms = ["RS256"]

        self.get_jwks_uri = get_jwks_uri
        self.jwks_uri = ""
        self.algorithms = algorithms
        self.public_keys: dict[str, provider_models.JSONWebKey] = {}
        self.key_refresh_interval = key_refresh_interval
        self.public_keys_last_refreshed: float = 0

    def keys_need_refresh(self) -> bool:
        return (
            time.time() - self.public_keys_last_refreshed
        ) > self.key_refresh_interval

    def refresh_keys(self) -> None:
        if not self.jwks_uri:
            self.jwks_uri = self.get_jwks_uri()
        try:
            resp = requests.get(
                self.jwks_uri, timeout=config["requests"]["timeout"]
            )
        except Exception:
            log.error("Could not retrieve JWKS data from %s", self.jwks_uri)
            return
        jwks = models.JSONWebKeySet.parse_raw(resp.text)
        self.public_keys_last_refreshed = time.time()
        self.public_keys.clear()
        for key in jwks.keys:
            self.public_keys[key.kid] = key

    def key_for_token(
        self, token: str, *, in_retry: int = 0
    ) -> provider_models.JSONWebKey:
        # Before we do anything, the validation keys may need to be refreshed.
        # If so, refresh them.
        if self.keys_need_refresh():
            self.refresh_keys()

        # Try to extract the claims from the token so that we can use the key ID
        # to determine which key we should use to validate the token.
        try:
            unverified_claims = jwt.get_unverified_header(token)
        except Exception:
            raise models.InvalidTokenError("Unable to parse key ID from token")
        # See if we have the key identified by this key ID.

        try:
            return self.public_keys[unverified_claims["kid"]]
        except KeyError:
            # If we don't have this key and this is the first attempt (ie: we
            # haven't refreshed keys yet), then try to refresh the keys and try
            # again.
            if in_retry:
                raise models.KeyIDNotFoundError()
            self.refresh_keys()
            return self.key_for_token(token, in_retry=1)


def _get_jwks_uri(wellknown_endpoint=cfg["endpoints"]["wellKnown"]):
    openid_config = requests.get(
        wellknown_endpoint,
        timeout=config["requests"]["timeout"],
    ).json()
    return openid_config["jwks_uri"]


# Our "singleton" key store:
KeyStore = _KeyStore(get_jwks_uri=_get_jwks_uri)
