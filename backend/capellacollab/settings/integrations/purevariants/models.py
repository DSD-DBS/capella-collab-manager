# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import logging

import pydantic
import requests
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core import pydantic as core_pydantic

log = logging.getLogger(__name__)


def validate_license_url(value: str | None):
    if value:
        try:
            requests.Request("GET", value).prepare()
        except requests.RequestException:
            log.info("Floating license validation failed", exc_info=True)
            raise ValueError(
                "The provided floating license server is not valid."
            )
    return value


class DatabasePureVariantsLicenses(database.Base):
    __tablename__ = "pure_variants"

    id: orm.Mapped[int] = orm.mapped_column(
        init=False, primary_key=True, index=True
    )
    license_server_url: orm.Mapped[str | None]
    license_key_filename: orm.Mapped[str | None]


class PureVariantsLicenses(core_pydantic.BaseModel):
    license_server_url: str | None = None
    license_key_filename: str | None = None

    _validate_value = pydantic.field_validator("license_server_url")(
        validate_license_url
    )
