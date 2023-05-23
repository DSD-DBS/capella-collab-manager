# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import logging

import pydantic
import requests
from pydantic import BaseModel
from requests import RequestException
from sqlalchemy.orm import Mapped, mapped_column

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

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    license_server_url: Mapped[str | None]
    license_key_filename: Mapped[str | None]


class PureVariantsLicenses(BaseModel):
    license_server_url: str | None
    license_key_filename: str | None

    _validate_value = pydantic.validator(
        "license_server_url", allow_reuse=True
    )(validate_license_url)

    class Config:
        orm_mode = True
