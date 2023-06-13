# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.tools import injectables
from capellacollab.tools.models import Tool
from capellacollab.users import models as users_model

from . import crud, models

router = fastapi.APIRouter(
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_model.Role.ADMIN
            )
        )
    ]
)


@router.put("", response_model=models.ToolIntegrations)
def update_integrations(
    body: models.PatchToolIntegrations,
    tool: "Tool" = fastapi.Depends(injectables.get_existing_tool),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.DatabaseToolIntegrations:
    return crud.update_integrations(db, tool.integrations, body)
