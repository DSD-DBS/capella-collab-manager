# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

# SPDX-FileCopyrightText: Marpaia and contributors
# SPDX-License-Identifier: Apache-2.0

# pylint: skip-file


import logging
import time
import typing as t

import jwt
import requests

from capellacollab.config import config

from . import flow, models

log = logging.getLogger(__name__)

auth_config = config.authentication


# Copied and adapted from https://github.com/marpaia/jwks/blob/master/jwks/jwks.py:


class _KeyStore:
    def __init__(
        self,
        *,
        algorithms: list[str] | None = None,
        key_refresh_interval=3600,
    ):
        if not algorithms:
            algorithms = ["RS256"]

        self.jwks_uri = flow.get_auth_endpoints()["jwks_uri"]
        self.algorithms = algorithms
        self.public_keys: dict[str, models.JSONWebKey] = {}
        self.key_refresh_interval = key_refresh_interval
        self.public_keys_last_refreshed: float = 0

    def keys_need_refresh(self) -> bool:
        return (
            time.time() - self.public_keys_last_refreshed
        ) > self.key_refresh_interval

    def refresh_keys(self) -> None:
        try:
            resp = requests.get(self.jwks_uri, timeout=config.requests.timeout)
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
    ) -> models.JSONWebKey:
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


# Our "singleton" key store:
KeyStore = _KeyStore()


def get_jwk_cfg(token: str) -> dict[str, t.Any]:
    return {
        "algorithms": ["RS256"],
        "audience": auth_config.audience or auth_config.client.id,
        "key": KeyStore.key_for_token(token).model_dump(),
    }
