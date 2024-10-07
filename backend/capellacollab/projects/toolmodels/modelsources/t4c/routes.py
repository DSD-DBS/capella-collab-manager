# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from collections import abc

import fastapi
from sqlalchemy import exc, orm

from capellacollab.core import database, responses
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.projects.toolmodels import (
    injectables as toolmodels_injectables,
)
from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.projects.toolmodels.backups import crud as backups_crud
from capellacollab.projects.users import models as projects_users_models
from capellacollab.settings.modelsources.t4c.instance import (
    injectables as settings_t4c_injectables,
)
from capellacollab.settings.modelsources.t4c.instance.repositories import (
    injectables as settings_t4c_repositories_injectables,
)
from capellacollab.users import models as users_models

from . import crud, exceptions, injectables, models, util

router = fastapi.APIRouter(
    dependencies=[
        fastapi.Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=projects_users_models.ProjectUserRole.MANAGER
            )
        )
    ],
    responses=responses.api_exceptions(
        minimum_project_role=projects_users_models.ProjectUserRole.MANAGER
    ),
)


@router.get(
    "",
    response_model=list[models.T4CModel],
)
def list_t4c_models(
    model: toolmodels_models.DatabaseToolModel = fastapi.Depends(
        toolmodels_injectables.get_existing_capella_model
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> abc.Sequence[models.DatabaseT4CModel]:
    return crud.get_t4c_models_for_tool_model(db, model)


@router.get(
    "/{t4c_model_id}",
    response_model=models.T4CModel,
    responses=responses.api_exceptions(
        [
            exceptions.T4CIntegrationNotFoundError(-1),
            exceptions.T4CIntegrationDoesntBelongToModel(-1, "test"),
        ],
    ),
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
    model: toolmodels_models.DatabaseToolModel = fastapi.Depends(
        toolmodels_injectables.get_existing_capella_model
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    instance = settings_t4c_injectables.get_existing_unarchived_instance(
        body.t4c_instance_id, db
    )
    repository = (
        settings_t4c_repositories_injectables.get_existing_t4c_repository(
            body.t4c_repository_id, db, instance
        )
    )

    util.verify_compatibility_of_model_and_server(
        model.name, model.version, repository
    )

    try:
        return crud.create_t4c_model(db, model, repository, body.name)
    except exc.IntegrityError:
        raise exceptions.T4CIntegrationAlreadyExists()


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
    responses=responses.api_exceptions(
        [
            exceptions.T4CIntegrationNotFoundError(-1),
            exceptions.T4CIntegrationDoesntBelongToModel(-1, "test"),
        ],
    ),
)
def update_t4c_model(
    body: models.PatchT4CModel,
    t4c_model: models.DatabaseT4CModel = fastapi.Depends(
        injectables.get_existing_t4c_model
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    if body.t4c_instance_id is not None:
        instance = settings_t4c_injectables.get_existing_unarchived_instance(
            body.t4c_instance_id, db
        )
    else:
        instance = t4c_model.repository.instance

    repository = (
        settings_t4c_repositories_injectables.get_existing_t4c_repository(
            body.t4c_repository_id or t4c_model.repository.id, db, instance
        )
    )

    util.verify_compatibility_of_model_and_server(
        t4c_model.model.name, t4c_model.model.version, repository
    )

    return crud.patch_t4c_model(db, t4c_model, repository, body.name)


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
    responses=responses.api_exceptions(
        [
            exceptions.T4CIntegrationNotFoundError(-1),
            exceptions.T4CIntegrationDoesntBelongToModel(-1, "test"),
        ],
    ),
)
def delete_t4c_model(
    t4c_model: models.DatabaseT4CModel = fastapi.Depends(
        injectables.get_existing_t4c_model
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    if backups_crud.get_pipelines_for_t4c_model(db, t4c_model):
        raise exceptions.T4CIntegrationUsedInPipelines()

    crud.delete_t4c_model(db, t4c_model)
