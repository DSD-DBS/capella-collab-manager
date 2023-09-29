# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

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


router = fastapi.APIRouter()
cfg: dict[str, str | None] = config["general"].get("metadata", {})


@router.get(
    "/metadata",
    response_model=Metadata,
)
def get_metadata():
    return Metadata(
        version=capellacollab.__version__,
        privacy_policy_url=cfg.get("privacyPolicyURL"),
        imprint_url=cfg.get("imprintURL"),
        provider=cfg.get("provider"),
        authentication_provider=cfg.get("authenticationProvider"),
        environment=cfg.get("environment"),
    )
