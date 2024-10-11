# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.projects import injectables as projects_injectables
from capellacollab.projects import models as projects_models
from capellacollab.projects.toolmodels import (
    injectables as toolmodels_injectables,
)
from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.projects.users import models as projects_users_models

from . import crud, exceptions, injectables, models

router = fastapi.APIRouter(
    dependencies=[
        fastapi.Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=projects_users_models.ProjectUserRole.USER
            )
        )
    ],
)


@router.get("", response_model=models.ModelProvisioning | None)
def get_provisioning(
    provisioning: models.DatabaseModelProvisioning = fastapi.Depends(
        injectables.get_model_provisioning
    ),
) -> models.DatabaseModelProvisioning:
    return provisioning


@router.delete("", status_code=204)
def reset_provisioning(
    provisioning: models.DatabaseModelProvisioning | None = fastapi.Depends(
        injectables.get_model_provisioning
    ),
    model: toolmodels_models.DatabaseToolModel = fastapi.Depends(
        toolmodels_injectables.get_existing_capella_model
    ),
    project: projects_models.DatabaseProject = fastapi.Depends(
        projects_injectables.get_existing_project
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    """This will delete the provisioning data from the workspace.
    During the next session request, the existing provisioning will be overwritten in the workspace.
    """
    if not provisioning:
        raise exceptions.ProvisioningNotFoundError(
            project_slug=project.slug, model_slug=model.slug
        )

    crud.delete_model_provisioning(db, provisioning)
