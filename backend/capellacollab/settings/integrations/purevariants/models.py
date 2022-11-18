# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import logging
import typing as t

import pydantic
import requests
from pydantic import BaseModel
from requests import RequestException
from sqlalchemy import Column, String

from capellacollab.core.database import Base

log = logging.getLogger(__name__)


def validate_license_url(value: t.Optional[str]):
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
    __tablename__ = "pure_variants_license"

    value = Column(String, primary_key=True)

    _validate_value = pydantic.validator("value", allow_reuse=True)(
        validate_license_url
    )


class PureVariantsLicenses(BaseModel):
    value: str

    class Config:
        orm_mode = True
