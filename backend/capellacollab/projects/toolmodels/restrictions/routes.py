# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.projects.toolmodels import (
    injectables as toolmodels_injectables,
)
from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.users import models as users_models

from . import crud, exceptions, injectables, models

router = fastapi.APIRouter(
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.ADMIN
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
    if body.allow_pure_variants and not model.tool.integrations.pure_variants:
        raise exceptions.PureVariantsIntegrationDisabledError()

    return crud.update_model_restrictions(db, restrictions, body)
