# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from collections import abc

import fastapi
from fastapi import status
from sqlalchemy import exc, orm

from capellacollab.core import database
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.projects.toolmodels import (
    injectables as toolmodels_injectables,
)
from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.projects.toolmodels.backups import crud as backups_crud
from capellacollab.projects.users import models as projects_users_models
from capellacollab.settings.modelsources.t4c import (
    injectables as settings_t4c_injecatbles,
)
from capellacollab.settings.modelsources.t4c.repositories import (
    injectables as settings_t4c_repositories_injectables,
)
from capellacollab.users import models as users_models

from . import crud, injectables, models

router = fastapi.APIRouter(
    dependencies=[
        fastapi.Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=projects_users_models.ProjectUserRole.MANAGER
            )
        )
    ],
)


@router.get(
    "",
    response_model=list[models.T4CModel],
)
def list_t4c_models(
    model: toolmodels_models.DatabaseCapellaModel = fastapi.Depends(
        toolmodels_injectables.get_existing_capella_model
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> abc.Sequence[models.DatabaseT4CModel]:
    return crud.get_t4c_models_for_tool_model(db, model)


@router.get(
    "/{t4c_model_id}",
    response_model=models.T4CModel,
)
def get_t4c_model(
    t4c_model: models.DatabaseT4CModel = fastapi.Depends(
        injectables.get_existing_t4c_model
    ),
) -> models.DatabaseT4CModel:
    return t4c_model


@router.post(
    "",
    response_model=models.T4CModel,
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.ADMIN
            )
        )
    ],
)
def create_t4c_model(
    body: models.SubmitT4CModel,
    model: toolmodels_models.DatabaseCapellaModel = fastapi.Depends(
        toolmodels_injectables.get_existing_capella_model
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    instance = settings_t4c_injecatbles.get_existing_unarchived_instance(
        body.t4c_instance_id, db
    )
    repository = (
        settings_t4c_repositories_injectables.get_existing_t4c_repository(
            body.t4c_repository_id, db, instance
        )
    )
    try:
        return crud.create_t4c_model(db, model, repository, body.name)
    except exc.IntegrityError as e:
        raise fastapi.HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"reason": "The model has been added already."},
        ) from e


@router.patch(
    "/{t4c_model_id}",
    response_model=models.T4CModel,
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.ADMIN
            )
        )
    ],
)
def edit_t4c_model(
    body: models.SubmitT4CModel,
    t4c_model: models.DatabaseT4CModel = fastapi.Depends(
        injectables.get_existing_t4c_model
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    return crud.patch_t4c_model(db, t4c_model, body)


@router.delete(
    "/{t4c_model_id}",
    status_code=204,
    dependencies=[
        fastapi.Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=projects_users_models.ProjectUserRole.MANAGER
            )
        )
    ],
)
def delete_t4c_model(
    t4c_model: models.DatabaseT4CModel = fastapi.Depends(
        injectables.get_existing_t4c_model
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    if backups_crud.get_pipelines_for_t4c_model(db, t4c_model):
        raise fastapi.HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "err_code": "T4C_MODEL_USED_FOR_BACKUP",
                "reason": "The t4c model can't be deleted: it's used for backup jobs",
            },
        )

    crud.delete_t4c_model(db, t4c_model)
