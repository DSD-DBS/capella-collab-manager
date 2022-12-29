# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseModel


class JSONWebKey(BaseModel):
    # alg: str
    kty: str
    use: str
    n: str
    e: str
    kid: str
    x5t: str
    x5c: list[str]


class JSONWebKeySet(BaseModel):
    keys: list[JSONWebKey]


class InvalidTokenError(Exception):
    pass


class KeyIDNotFoundError(Exception):
    pass
