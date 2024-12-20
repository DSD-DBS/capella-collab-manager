# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.projects.toolmodels import (
    injectables as toolmodels_injectables,
)
from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.projects.toolmodels.backups import crud as backups_crud
from capellacollab.projects.users import models as projects_users_models
from capellacollab.settings.modelsources.git import core as instances_git_core
from capellacollab.settings.modelsources.git import models as git_models
from capellacollab.settings.modelsources.git import util as git_util

from . import crud, exceptions, injectables, models
from .handler import cache

router = fastapi.APIRouter()
log = logging.getLogger(__name__)


@router.get("", response_model=list[models.GitModel])
def get_git_models(
    capella_model: toolmodels_models.DatabaseToolModel = fastapi.Depends(
        toolmodels_injectables.get_existing_capella_model
    ),
) -> list[models.DatabaseGitModel]:
    return capella_model.git_models


@router.get(
    "/{git_model_id}",
    response_model=models.GitModel,
    dependencies=[
        fastapi.Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=projects_users_models.ProjectUserRole.MANAGER
            )
        )
    ],
)
def get_git_model_by_id(
    git_model: models.DatabaseGitModel = fastapi.Depends(
        injectables.get_existing_git_model
    ),
) -> models.DatabaseGitModel:
    return git_model


@router.get(
    "/primary/revisions",
    response_model=git_models.GetRevisionsResponseModel,
    dependencies=[
        fastapi.Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=projects_users_models.ProjectUserRole.MANAGER
            )
        )
    ],
)
async def get_revisions_of_primary_git_model(
    primary_git_model: models.DatabaseGitModel = fastapi.Depends(
        injectables.get_existing_primary_git_model
    ),
) -> git_models.GetRevisionsResponseModel:
    return await instances_git_core.get_remote_refs(
        primary_git_model.path,
        primary_git_model.username,
        primary_git_model.password,
        default=primary_git_model.revision,
    )


@router.post(
    "/{git_model_id}/revisions",
    response_model=git_models.GetRevisionsResponseModel,
    dependencies=[
        fastapi.Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=projects_users_models.ProjectUserRole.USER
            )
        )
    ],
)
async def get_revisions_with_model_credentials(
    url: str = fastapi.Body(media_type="text/plain"),
    git_model: models.DatabaseGitModel = fastapi.Depends(
        injectables.get_existing_git_model
    ),
):
    return await instances_git_core.get_remote_refs(
        url, git_model.username, git_model.password
    )


@router.post(
    "",
    response_model=models.GitModel,
    dependencies=[
        fastapi.Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=projects_users_models.ProjectUserRole.MANAGER
            )
        )
    ],
)
def create_git_model(
    post_git_model: models.PostGitModel,
    capella_model: toolmodels_models.DatabaseToolModel = fastapi.Depends(
        toolmodels_injectables.get_existing_capella_model
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.DatabaseGitModel:
    git_util.verify_path_prefix(db, post_git_model.path)

    new_git_model = crud.add_git_model_to_capellamodel(
        db, capella_model, post_git_model
    )
    return new_git_model


@router.put(
    "/{git_model_id}",
    response_model=models.GitModel,
    dependencies=[
        fastapi.Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=projects_users_models.ProjectUserRole.MANAGER
            )
        )
    ],
)
def update_git_model_by_id(
    put_git_model: models.PutGitModel,
    db_git_model: models.DatabaseGitModel = fastapi.Depends(
        injectables.get_existing_git_model
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.DatabaseGitModel:
    git_util.verify_path_prefix(db, put_git_model.path)
    cache.GitValkeyCache(git_model_id=db_git_model.id).clear()
    return crud.update_git_model(db, db_git_model, put_git_model)


@router.delete("/cache")
def empty_cache(
    git_model: models.DatabaseGitModel = fastapi.Depends(
        injectables.get_existing_primary_git_model
    ),
):
    cache.GitValkeyCache(git_model_id=git_model.id).clear()


@router.delete(
    "/{git_model_id}",
    status_code=204,
    dependencies=[
        fastapi.Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=projects_users_models.ProjectUserRole.MANAGER
            )
        )
    ],
)
def delete_git_model_by_id(
    db_git_model: models.DatabaseGitModel = fastapi.Depends(
        injectables.get_existing_git_model
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    if backups_crud.get_pipelines_for_git_model(db, db_git_model):
        raise exceptions.GitRepositoryUsedInPipelines(db_git_model.id)
    cache.GitValkeyCache(git_model_id=db_git_model.id).clear()
    crud.delete_git_model(db, db_git_model)
