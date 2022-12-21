# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from capellacollab.core.authentication.database import ProjectRoleVerification
from capellacollab.core.database import Base, get_db
from capellacollab.projects.users.models import ProjectUserRole

from .. import crud
from ..injectables import get_existing_capella_model
from ..models import DatabaseCapellaModel
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
    model: DatabaseCapellaModel = Depends(get_existing_capella_model),
    db: Session = Depends(get_db),
) -> ToolModelRestrictions:
    if not model.tool.integrations.pure_variants:
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "The tool of this model has no pure::variants integration."
                "Please enable the pure::variants integration in the settings first.",
            },
        )
    model.restrict_pv = body.pv
    crud.commit_model(db, model)
    return model
