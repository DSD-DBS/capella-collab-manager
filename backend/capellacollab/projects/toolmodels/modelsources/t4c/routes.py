# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t
from collections import abc

import fastapi
from sqlalchemy import exc, orm

from capellacollab.core import database, responses
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
from capellacollab.projects.toolmodels.backups import crud as backups_crud
from capellacollab.settings.modelsources.t4c.instance import (
    injectables as settings_t4c_injectables,
)
from capellacollab.settings.modelsources.t4c.instance.repositories import (
    injectables as settings_t4c_repositories_injectables,
)

from . import crud, exceptions, injectables, models, util

router = fastapi.APIRouter()


@router.get(
    "",
    response_model=list[models.SimpleT4CModelWithRepository],
    dependencies=[
        fastapi.Depends(
            projects_permissions_injectables.ProjectPermissionValidation(
                required_scope=projects_permissions_models.ProjectUserScopes(
                    t4c_model_links={permissions_models.UserTokenVerb.GET}
                )
            )
        )
    ],
)
def list_t4c_models(
    model: t.Annotated[toolmodels_models.DatabaseToolModel, fastapi.Depends(
        toolmodels_injectables.get_existing_capella_model
    )],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
) -> abc.Sequence[models.DatabaseT4CModel]:
    return crud.get_t4c_models_for_tool_model(db, model)


@router.get(
    "/{t4c_model_id}",
    response_model=models.SimpleT4CModelWithRepository,
    responses=responses.translate_exceptions_to_openapi_schema(
        [
            exceptions.T4CIntegrationNotFoundError,
            exceptions.T4CIntegrationDoesntBelongToModel,
        ],
    ),
    dependencies=[
        fastapi.Depends(
            projects_permissions_injectables.ProjectPermissionValidation(
                required_scope=projects_permissions_models.ProjectUserScopes(
                    t4c_model_links={permissions_models.UserTokenVerb.GET}
                )
            )
        )
    ],
)
def get_t4c_model(
    t4c_model: t.Annotated[models.DatabaseT4CModel, fastapi.Depends(
        injectables.get_existing_t4c_model
    )],
) -> models.DatabaseT4CModel:
    return t4c_model


@router.post(
    "",
    response_model=models.SimpleT4CModelWithRepository,
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        t4c_repositories={
                            permissions_models.UserTokenVerb.UPDATE
                        }
                    )
                )
            ),
        ),
        fastapi.Depends(
            projects_permissions_injectables.ProjectPermissionValidation(
                required_scope=projects_permissions_models.ProjectUserScopes(
                    t4c_model_links={permissions_models.UserTokenVerb.CREATE}
                )
            )
        ),
    ],
)
def create_t4c_model(
    body: models.SubmitT4CModel,
    model: t.Annotated[toolmodels_models.DatabaseToolModel, fastapi.Depends(
        toolmodels_injectables.get_existing_capella_model
    )],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
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
    except exc.IntegrityError as e:
        raise exceptions.T4CIntegrationAlreadyExists() from e


@router.patch(
    "/{t4c_model_id}",
    response_model=models.SimpleT4CModelWithRepository,
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        t4c_repositories={
                            permissions_models.UserTokenVerb.UPDATE
                        }
                    )
                )
            ),
        ),
        fastapi.Depends(
            projects_permissions_injectables.ProjectPermissionValidation(
                required_scope=projects_permissions_models.ProjectUserScopes(
                    t4c_model_links={permissions_models.UserTokenVerb.UPDATE}
                )
            )
        ),
    ],
    responses=responses.translate_exceptions_to_openapi_schema(
        [
            exceptions.T4CIntegrationNotFoundError,
            exceptions.T4CIntegrationDoesntBelongToModel,
        ],
    ),
)
def update_t4c_model(
    body: models.PatchT4CModel,
    t4c_model: t.Annotated[models.DatabaseT4CModel, fastapi.Depends(
        injectables.get_existing_t4c_model
    )],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
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
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        t4c_repositories={
                            permissions_models.UserTokenVerb.UPDATE
                        }
                    )
                )
            ),
        ),
        fastapi.Depends(
            projects_permissions_injectables.ProjectPermissionValidation(
                required_scope=projects_permissions_models.ProjectUserScopes(
                    t4c_model_links={permissions_models.UserTokenVerb.DELETE}
                )
            )
        ),
    ],
    responses=responses.translate_exceptions_to_openapi_schema(
        [
            exceptions.T4CIntegrationNotFoundError,
            exceptions.T4CIntegrationDoesntBelongToModel,
        ],
    ),
)
def delete_t4c_model(
    t4c_model: t.Annotated[models.DatabaseT4CModel, fastapi.Depends(
        injectables.get_existing_t4c_model
    )],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
):
    if backups_crud.get_pipelines_for_t4c_model(db, t4c_model):
        raise exceptions.T4CIntegrationUsedInPipelines()

    crud.delete_t4c_model(db, t4c_model)
