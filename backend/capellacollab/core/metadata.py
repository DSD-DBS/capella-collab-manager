# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

import fastapi
import pydantic

import capellacollab
from capellacollab.config import config


class Metadata(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    version: str
    privacy_policy_url: str | None
    imprint_url: str | None
    provider: str | None
    authentication_provider: str | None
    environment: str | None

    host: str | None
    port: str | None
    protocol: str | None


router = fastapi.APIRouter()

general_cfg: dict[str, t.Any] = config["general"]
metadata_cfg: dict[str, str | None] = general_cfg.get("metadata", {})


@router.get(
    "/metadata",
    response_model=Metadata,
)
def get_metadata():
    return Metadata(
        version=capellacollab.__version__,
        privacy_policy_url=metadata_cfg.get("privacyPolicyURL"),
        imprint_url=metadata_cfg.get("imprintURL"),
        provider=metadata_cfg.get("provider"),
        authentication_provider=metadata_cfg.get("authenticationProvider"),
        environment=metadata_cfg.get("environment"),
        host=general_cfg.get("host"),
        port=str(general_cfg.get("port")),
        protocol=general_cfg.get("scheme"),
    )
