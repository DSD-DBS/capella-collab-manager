# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


from capellacollab.core import pydantic as core_pydantic


class TokenRequest(core_pydantic.BaseModel):
    code: str
    nonce: str
    code_verifier: str
