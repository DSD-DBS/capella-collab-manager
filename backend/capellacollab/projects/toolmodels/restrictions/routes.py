# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.core.database import get_db
from capellacollab.projects.users.models import ProjectUserRole

from ..injectables import get_existing_capella_model
from ..models import DatabaseCapellaModel, DatabaseToolModelRestrictions
from . import crud
from .injectables import get_model_restrictions
from .models import ToolModelRestrictions

router = APIRouter(
    dependencies=[
        Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=ProjectUserRole.ADMIN
            )
        )
    ],
)


@router.get("", response_model=ToolModelRestrictions)
def get_restrictions(
    restrictions: DatabaseToolModelRestrictions = Depends(
        get_model_restrictions
    ),
) -> DatabaseToolModelRestrictions:
    return restrictions


@router.patch("", response_model=ToolModelRestrictions)
def update_restrictions(
    body: ToolModelRestrictions,
    restrictions: DatabaseToolModelRestrictions = Depends(
        get_model_restrictions
    ),
    model: DatabaseCapellaModel = Depends(get_existing_capella_model),
    db: Session = Depends(get_db),
) -> DatabaseToolModelRestrictions:
    if body.allow_pure_variants and not model.tool.integrations.pure_variants:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "reason": "The tool of this model has no pure::variants integration."
                "Please enable the pure::variants integration in the settings first.",
            },
        )

    return crud.update_model_restrictions(db, restrictions, body)
