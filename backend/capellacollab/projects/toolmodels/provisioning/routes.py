# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.permissions import models as permissions_models
from capellacollab.projects import injectables as projects_injectables
from capellacollab.projects import models as projects_models
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
    response_model=models.ModelProvisioning | None,
    dependencies=[
        fastapi.Depends(
            projects_permissions_injectables.ProjectPermissionValidation(
                required_scope=projects_permissions_models.ProjectUserScopes(
                    provisioning={permissions_models.UserTokenVerb.GET}
                )
            )
        )
    ],
)
def get_provisioning(
    provisioning: t.Annotated[
        models.DatabaseModelProvisioning,
        fastapi.Depends(injectables.get_model_provisioning),
    ],
) -> models.DatabaseModelProvisioning:
    return provisioning


@router.delete(
    "",
    status_code=204,
    dependencies=[
        fastapi.Depends(
            projects_permissions_injectables.ProjectPermissionValidation(
                required_scope=projects_permissions_models.ProjectUserScopes(
                    provisioning={permissions_models.UserTokenVerb.DELETE}
                )
            )
        )
    ],
)
def reset_provisioning(
    provisioning: t.Annotated[
        models.DatabaseModelProvisioning | None,
        fastapi.Depends(injectables.get_model_provisioning),
    ],
    model: t.Annotated[
        toolmodels_models.DatabaseToolModel,
        fastapi.Depends(toolmodels_injectables.get_existing_capella_model),
    ],
    project: t.Annotated[
        projects_models.DatabaseProject,
        fastapi.Depends(projects_injectables.get_existing_project),
    ],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
):
    """This will delete the provisioning data from the workspace.
    During the next session request, the existing provisioning will be overwritten in the workspace.
    """
    if not provisioning:
        raise exceptions.ProvisioningNotFoundError(
            project_slug=project.slug, model_slug=model.slug
        )

    crud.delete_model_provisioning(db, provisioning)
