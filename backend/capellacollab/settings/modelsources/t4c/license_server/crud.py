# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from collections import abc

import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.core import database

from . import exceptions, models


def get_t4c_license_servers(
    db: orm.Session,
) -> abc.Sequence[models.DatabaseT4CLicenseServer]:
    return (
        db.execute(sa.select(models.DatabaseT4CLicenseServer)).scalars().all()
    )


def get_t4c_license_server_by_id(
    db: orm.Session, license_server_id: int
) -> models.DatabaseT4CLicenseServer | None:
    return db.execute(
        sa.select(models.DatabaseT4CLicenseServer).where(
            models.DatabaseT4CLicenseServer.id == license_server_id
        )
    ).scalar_one_or_none()


def get_t4c_license_server_by_name(
    db: orm.Session, license_server_name: str
) -> models.DatabaseT4CLicenseServer | None:
    return db.execute(
        sa.select(models.DatabaseT4CLicenseServer).where(
            models.DatabaseT4CLicenseServer.name == license_server_name
        )
    ).scalar_one_or_none()


def create_t4c_license_server(
    db: orm.Session, license_server: models.DatabaseT4CLicenseServer
) -> models.DatabaseT4CLicenseServer:
    db.add(license_server)
    db.commit()
    return license_server


def update_t4c_license_server(
    db: orm.Session,
    license_server: models.DatabaseT4CLicenseServer,
    patch_t4c_instance: models.PatchT4CLicenseServer,
):
    database.patch_database_with_pydantic_object(
        license_server, patch_t4c_instance
    )

    db.commit()

    return license_server


def delete_t4c_license_server(
    db: orm.Session,
    license_server: models.DatabaseT4CLicenseServer,
):
    if len(license_server.instances) > 0:
        raise exceptions.T4CLicenseServerInUseError(license_server.id)
    db.delete(license_server)
    db.commit()
