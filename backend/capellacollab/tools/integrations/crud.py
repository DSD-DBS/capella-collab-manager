# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from sqlalchemy.orm import Session

from capellacollab.core.database import patch_database_with_pydantic_object

from .models import DatabaseToolIntegrations, PatchToolIntegrations


def update_integrations(
    db: Session,
    integrations: DatabaseToolIntegrations,
    patch_integrations: PatchToolIntegrations,
) -> DatabaseToolIntegrations:
    patch_database_with_pydantic_object(integrations, patch_integrations)

    db.commit()
    return integrations
