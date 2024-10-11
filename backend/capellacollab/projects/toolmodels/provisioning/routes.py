# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.projects.users import models as projects_users_models

from . import crud, injectables, models

router = fastapi.APIRouter(
    dependencies=[
        fastapi.Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=projects_users_models.ProjectUserRole.USER
            )
        )
    ],
)


@router.get("", response_model=models.ModelProvisioning)
def get_provisioning(
    provisioning: models.DatabaseModelProvisioning = fastapi.Depends(
        injectables.get_model_provisioning
    ),
) -> models.DatabaseModelProvisioning:
    return provisioning


@router.delete("", status_code=204)
def reset_provisioning(
    provisioning: models.DatabaseModelProvisioning = fastapi.Depends(
        injectables.get_model_provisioning
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    """This will delete the provisioning data from the workspace.
    During the next session request, the existing provisioning will be overwritten in the workspace.
    """

    crud.delete_project_provisioning(db, provisioning)
