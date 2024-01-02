# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from sqlalchemy import orm

from capellacollab.core import database

from . import models


def update_integrations(
    db: orm.Session,
    integrations: models.DatabaseToolIntegrations,
    patch_integrations: models.PatchToolIntegrations,
) -> models.DatabaseToolIntegrations:
    database.patch_database_with_pydantic_object(
        integrations, patch_integrations
    )

    db.commit()
    return integrations
