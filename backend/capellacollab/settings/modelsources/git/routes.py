# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from collections import abc

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.settings.modelsources.git import core as git_core
from capellacollab.users import models as users_models

from . import crud, injectables, models, util

router = fastapi.APIRouter()


@router.get("", response_model=list[models.GitInstance])
def list_git_instances(
    db: orm.Session = fastapi.Depends(database.get_db),
) -> abc.Sequence[models.DatabaseGitInstance]:
    return crud.get_git_instances(db)


@router.get(
    "/{git_instance_id}",
    response_model=models.GitInstance,
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.ADMIN
            )
        )
    ],
)
def get_git_instance(
    git_instance: models.DatabaseGitInstance = fastapi.Depends(
        injectables.get_existing_git_instance
    ),
):
    return git_instance


@router.post(
    "",
    response_model=models.GitInstance,
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.ADMIN
            )
        )
    ],
)
def create_git_instance(
    post_git_instance: models.PostGitInstance,
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.DatabaseGitInstance:
    return crud.create_git_instance(db, post_git_instance)


@router.patch(
    "/{git_instance_id}",
    response_model=models.GitInstance,
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.ADMIN
            )
        )
    ],
)
def edit_git_instance(
    put_git_instance: models.PostGitInstance,
    db_git_instance: models.DatabaseGitInstance = fastapi.Depends(
        injectables.get_existing_git_instance
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.DatabaseGitInstance:
    return crud.update_git_instance(db, db_git_instance, put_git_instance)


@router.delete(
    "/{git_instance_id}",
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.ADMIN
            )
        )
    ],
)
def delete_git_instances(
    git_instance: models.DatabaseGitInstance = fastapi.Depends(
        injectables.get_existing_git_instance
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    return crud.delete_git_instance(db, git_instance)


# In the future, check if the HTTP QUERY method is available in fast api,
# and if so, use it instead of POST
# (https://www.ietf.org/archive/id/draft-ietf-httpbis-safe-method-w-body-02.html)
@router.post("/revisions", response_model=models.GetRevisionsResponseModel)
async def get_revisions(
    body: models.GetRevisionModel,
) -> models.GetRevisionsResponseModel:
    url = body.url
    username = body.credentials.username
    password = body.credentials.password

    return await git_core.get_remote_refs(url, username, password)


@router.post("/validate/path", response_model=bool)
def validate_path(
    body: models.PathValidation,
    db: orm.Session = fastapi.Depends(database.get_db),
) -> bool:
    try:
        util.verify_path_prefix(db, body.url)
        return True
    except Exception:
        return False
