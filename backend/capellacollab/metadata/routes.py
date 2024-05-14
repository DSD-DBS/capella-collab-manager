# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from sqlalchemy import orm

import capellacollab
from capellacollab.config import config
from capellacollab.core import database
from capellacollab.core import pydantic as core_pydantic
from capellacollab.settings.configuration import core as config_core
from capellacollab.settings.configuration import (
    models as settings_config_models,
)


class Metadata(core_pydantic.BaseModel):
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


@router.get(
    "/metadata",
    response_model=Metadata,
)
def get_metadata(db: orm.Session = fastapi.Depends(database.get_db)):
    cfg = config_core.get_config(db, "global")
    assert isinstance(cfg, settings_config_models.GlobalConfiguration)

    return Metadata.model_validate(
        cfg.metadata.model_dump()
        | {
            "version": capellacollab.__version__,
            "host": config.general.host,
            "port": str(config.general.port),
            "protocol": config.general.scheme,
        }
    )
