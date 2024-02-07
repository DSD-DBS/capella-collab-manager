# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from fastapi import status
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.projects.toolmodels import (
    injectables as toolmodels_injectables,
)
from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.projects.users import models as projects_users_models

from . import crud, injectables, models

router = fastapi.APIRouter(
    dependencies=[
        fastapi.Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=projects_users_models.ProjectUserRole.ADMIN
            )
        )
    ],
)


@router.get("", response_model=models.ToolModelRestrictions)
def get_restrictions(
    restrictions: models.DatabaseToolModelRestrictions = fastapi.Depends(
        injectables.get_model_restrictions
    ),
) -> models.DatabaseToolModelRestrictions:
    return restrictions


@router.patch("", response_model=models.ToolModelRestrictions)
def update_restrictions(
    body: models.ToolModelRestrictions,
    restrictions: models.DatabaseToolModelRestrictions = fastapi.Depends(
        injectables.get_model_restrictions
    ),
    model: toolmodels_models.DatabaseToolModel = fastapi.Depends(
        toolmodels_injectables.get_existing_capella_model
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.DatabaseToolModelRestrictions:
    if (
        body.allow_pure_variants
        and model.tool.integrations
        and not model.tool.integrations.pure_variants
    ):
        raise fastapi.HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "reason": "The tool of this model has no pure::variants integration."
                "Please enable the pure::variants integration in the settings first.",
            },
        )

    return crud.update_model_restrictions(db, restrictions, body)
