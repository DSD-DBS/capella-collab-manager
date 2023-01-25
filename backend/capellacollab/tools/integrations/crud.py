# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from sqlalchemy.orm import Session

from capellacollab.core.database import patch_database_with_pydantic_object
from capellacollab.tools.models import Tool

from .models import DatabaseToolIntegrations, PatchToolIntegrations


def update_integrations(
    db: Session,
    existing_integrations: DatabaseToolIntegrations,
    patch_integrations: PatchToolIntegrations,
) -> Tool:
    patch_database_with_pydantic_object(
        db, existing_integrations, patch_integrations
    )
    db.commit()
    return existing_integrations


def intialize_new_integration_table(db: Session, tool: Tool):
    integrations = DatabaseToolIntegrations(pure_variants=False, t4c=False)
    tool.integrations = integrations
    db.commit()
