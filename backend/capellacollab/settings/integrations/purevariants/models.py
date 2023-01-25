# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import logging

import pydantic
import requests
from pydantic import BaseModel
from requests import RequestException
from sqlalchemy import Column, Integer, String

from capellacollab.core.database import Base

log = logging.getLogger(__name__)


def validate_license_url(value: str | None):
    if value:
        try:
            requests.Request("GET", value).prepare()
        except RequestException:
            log.info("Floating license validation failed", exc_info=True)
            raise ValueError(
                "The provided floating license server is not valid."
            )
    return value


class DatabasePureVariantsLicenses(Base):
    __tablename__ = "pure_variants"

    id: int = Column(Integer, primary_key=True, index=True)
    license_server_url = Column(String, nullable=True)
    license_key_filename = Column(String, nullable=True)


class PureVariantsLicenses(BaseModel):
    license_server_url: str | None
    license_key_filename: str | None

    _validate_value = pydantic.validator(
        "license_server_url", allow_reuse=True
    )(validate_license_url)

    class Config:
        orm_mode = True
