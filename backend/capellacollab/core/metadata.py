# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

import fastapi
import pydantic
from sqlalchemy import orm

import capellacollab
from capellacollab.config import config
from capellacollab.core import database
from capellacollab.settings.configuration import core as config_core
from capellacollab.settings.configuration import models as config_models


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


@router.get(
    "/metadata",
    response_model=Metadata,
)
def get_metadata(db: orm.Session = fastapi.Depends(database.get_db)):
    cfg = config_core.get_config(db, "global")
    assert isinstance(cfg, config_models.GlobalConfiguration)

    return Metadata.model_validate(
        cfg.metadata.model_dump()
        | {
            "version": capellacollab.__version__,
            "host": general_cfg.get("host"),
            "port": str(general_cfg.get("port")),
            "protocol": general_cfg.get("scheme"),
        }
    )
