# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

import fastapi
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import orm

import capellacollab
from capellacollab.config import config
from capellacollab.core import database
from capellacollab.settings.configuration import core as config_core
from capellacollab.settings.configuration import models as config_models


class Metadata(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    version: str = Field(
        description="The version of the application", examples=["1.0.0"]
    )
    privacy_policy_url: str | None = Field(
        description="The URL to the privacy policy",
        examples=["https://example.com/privacy-policy"],
    )
    imprint_url: str | None = Field(
        description="The URL to the imprint",
        examples=["https://example.com/imprint"],
    )
    provider: str | None = Field(
        description="The application provider",
        examples=["DB InfraGO AG"],
    )
    authentication_provider: str | None = Field(
        description="The authentication provider", examples=["OAuth2"]
    )
    environment: str | None = Field(
        description="The application environment", examples=["test"]
    )

    host: str | None = Field(
        description="The host of the application", examples=["localhost"]
    )
    port: str | None = Field(
        description="The port of the application", examples=["4200"]
    )
    protocol: str | None = Field(
        description="The protocol of the application", examples=["https"]
    )


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
