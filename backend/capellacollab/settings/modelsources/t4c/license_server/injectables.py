# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from sqlalchemy import orm

from capellacollab.core import database

from . import crud, exceptions, models


def get_existing_license_server(
    t4c_license_server_id: int,
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.DatabaseT4CLicenseServer:
    if license_server := crud.get_t4c_license_server_by_id(
        db, t4c_license_server_id
    ):
        return license_server

    raise exceptions.T4CLicenseServerNotFoundError(t4c_license_server_id)
