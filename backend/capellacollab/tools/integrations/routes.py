# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from capellacollab.core.authentication.database import RoleVerification
from capellacollab.core.database import get_db
from capellacollab.tools import injectables
from capellacollab.tools.models import Tool
from capellacollab.users.models import Role

from . import crud
from .models import PatchToolIntegrations, ToolIntegrations

router = APIRouter(
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))]
)


@router.put(
    "",
    response_model=ToolIntegrations,
)
def update_integrations(
    body: PatchToolIntegrations,
    tool: "Tool" = Depends(injectables.get_existing_tool),
    db: Session = Depends(get_db),
) -> ToolIntegrations:
    return crud.update_integrations(db, tool.integrations, body)
