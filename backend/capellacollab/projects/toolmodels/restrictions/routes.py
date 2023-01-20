# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from capellacollab.core import database
from capellacollab.core.authentication.database import ProjectRoleVerification
from capellacollab.core.database import get_db
from capellacollab.projects.users.models import ProjectUserRole

from ..injectables import get_existing_capella_model
from ..models import DatabaseCapellaModel
from .injectables import get_model_restrictions
from .models import ToolModelRestrictions

router = APIRouter(
    dependencies=[
        Depends(ProjectRoleVerification(required_role=ProjectUserRole.ADMIN))
    ],
)


@router.get("", response_model=ToolModelRestrictions)
def get_restrictions(
    model: DatabaseCapellaModel = Depends(get_existing_capella_model),
) -> ToolModelRestrictions:
    return model


@router.patch("", response_model=ToolModelRestrictions)
def update_restrictions(
    body: ToolModelRestrictions,
    restrictions: DatabaseCapellaModel = Depends(get_model_restrictions),
    model: DatabaseCapellaModel = Depends(get_existing_capella_model),
    db: Session = Depends(get_db),
) -> ToolModelRestrictions:
    if body.allow_pure_variants:
        if not model.tool.integrations.pure_variants:
            raise HTTPException(
                status_code=500,
                detail={
                    "reason": "The tool of this model has no pure::variants integration."
                    "Please enable the pure::variants integration in the settings first.",
                },
            )

    database.patch_database_with_pydantic_object(
        db, database_object=restrictions, pydantic_object=body
    )
    return restrictions
