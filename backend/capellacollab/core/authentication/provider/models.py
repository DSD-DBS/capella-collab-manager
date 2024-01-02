# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import pydantic


class JSONWebKey(pydantic.BaseModel):
    # alg: str
    kty: str
    use: str
    n: str
    e: str
    kid: str
    x5t: str | None = None
    x5c: list[str] | None = None


class JSONWebKeySet(pydantic.BaseModel):
    keys: list[JSONWebKey]


class InvalidTokenError(Exception):
    pass


class KeyIDNotFoundError(Exception):
    pass
