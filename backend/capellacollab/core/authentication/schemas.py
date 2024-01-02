# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


from pydantic import BaseModel


class TokenRequest(BaseModel):
    code: str
    state: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str
