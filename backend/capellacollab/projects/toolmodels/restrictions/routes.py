# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.permissions import injectables as permissions_injectables
from capellacollab.permissions import models as permissions_models
from capellacollab.projects.permissions import (
    injectables as projects_permissions_injectables,
)
from capellacollab.projects.permissions import (
    models as projects_permissions_models,
)
from capellacollab.projects.toolmodels import (
    injectables as toolmodels_injectables,
)
from capellacollab.projects.toolmodels import models as toolmodels_models

from . import crud, exceptions, injectables, models

router = fastapi.APIRouter()


@router.get(
    "",
    response_model=models.ToolModelRestrictions,
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        users={permissions_models.UserTokenVerb.GET}
                    )
                )
            ),
        ),
        fastapi.Depends(
            projects_permissions_injectables.ProjectPermissionValidation(
                required_scope=projects_permissions_models.ProjectUserScopes(
                    restrictions={permissions_models.UserTokenVerb.GET}
                )
            )
        ),
    ],
)
def get_restrictions(
    restrictions: t.Annotated[
        models.DatabaseToolModelRestrictions,
        fastapi.Depends(injectables.get_model_restrictions),
    ],
) -> models.DatabaseToolModelRestrictions:
    return restrictions


@router.patch(
    "",
    response_model=models.ToolModelRestrictions,
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        users={permissions_models.UserTokenVerb.UPDATE}
                    )
                )
            ),
        ),
        fastapi.Depends(
            projects_permissions_injectables.ProjectPermissionValidation(
                required_scope=projects_permissions_models.ProjectUserScopes(
                    restrictions={permissions_models.UserTokenVerb.UPDATE}
                )
            )
        ),
    ],
)
def update_restrictions(
    body: models.ToolModelRestrictions,
    restrictions: t.Annotated[
        models.DatabaseToolModelRestrictions,
        fastapi.Depends(injectables.get_model_restrictions),
    ],
    model: t.Annotated[
        toolmodels_models.DatabaseToolModel,
        fastapi.Depends(toolmodels_injectables.get_existing_capella_model),
    ],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
) -> models.DatabaseToolModelRestrictions:
    if body.allow_pure_variants and not model.tool.integrations.pure_variants:
        raise exceptions.PureVariantsIntegrationDisabledError()

    return crud.update_model_restrictions(db, restrictions, body)
