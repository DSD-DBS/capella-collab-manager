# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi

from capellacollab.permissions import models as permissions_models
from capellacollab.projects.permissions import (
    injectables as projects_permissions_injectables,
)
from capellacollab.projects.permissions import (
    models as projects_permissions_models,
)

from . import models

router = fastapi.APIRouter(
    prefix="/volumes",
    tags=["Projects - Volumes"],
)


@router.get(
    "",
    dependencies=[
        fastapi.Depends(
            projects_permissions_injectables.ProjectPermissionValidation(
                required_scope=projects_permissions_models.ProjectUserScopes(
                    project_users={permissions_models.UserTokenVerb.GET}
                )
            )
        )
    ],
)
def get_project_volumes() -> models.ProjectVolume:
    return []


@router.get(
    "",
    dependencies=[
        fastapi.Depends(
            projects_permissions_injectables.ProjectPermissionValidation(
                required_scope=projects_permissions_models.ProjectUserScopes(
                    project_users={permissions_models.UserTokenVerb.CREATE}
                )
            )
        )
    ],
)
def create_project_volume():
    return {}


@router.get(
    "",
    dependencies=[
        fastapi.Depends(
            projects_permissions_injectables.ProjectPermissionValidation(
                required_scope=projects_permissions_models.ProjectUserScopes(
                    project_users={permissions_models.UserTokenVerb.DELETE}
                )
            )
        )
    ],
)
def delete_project_volume():
    return {}
