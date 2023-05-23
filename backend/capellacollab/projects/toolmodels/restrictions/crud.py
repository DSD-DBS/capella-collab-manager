# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from sqlalchemy.orm import Session

from capellacollab.core.database import patch_database_with_pydantic_object

from . import models


def update_model_restrictions(
    db: Session,
    restrictions: models.DatabaseToolModelRestrictions,
    patch_restrictions: models.ToolModelRestrictions,
) -> models.DatabaseToolModelRestrictions:
    patch_database_with_pydantic_object(restrictions, patch_restrictions)

    db.commit()
    return restrictions
