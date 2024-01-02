# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from sqlalchemy import orm

from capellacollab.core import database

from . import models


def update_model_restrictions(
    db: orm.Session,
    restrictions: models.DatabaseToolModelRestrictions,
    patch_restrictions: models.ToolModelRestrictions,
) -> models.DatabaseToolModelRestrictions:
    database.patch_database_with_pydantic_object(
        restrictions, patch_restrictions
    )

    db.commit()
    return restrictions
