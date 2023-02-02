# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.core.database import get_db
from capellacollab.settings.modelsources.git import crud
from capellacollab.settings.modelsources.git.core import get_remote_refs
from capellacollab.settings.modelsources.git.injectables import (
    get_existing_git_setting,
)
from capellacollab.settings.modelsources.git.models import (
    DatabaseGitInstance,
    GetRevisionModel,
    GetRevisionsResponseModel,
    GitInstance,
    PostGitInstance,
)
from capellacollab.users.models import Role

router = APIRouter()


@router.get("/", response_model=list[GitInstance])
def list_git_settings(
    db: Session = Depends(get_db),
) -> list[DatabaseGitInstance]:
    return crud.get_git_settings(db)


@router.get(
    "/{git_setting_id}",
    response_model=GitInstance,
    dependencies=[
        Depends(auth_injectables.RoleVerification(required_role=Role.ADMIN))
    ],
)
def get_git_setting(
    git_setting: DatabaseGitInstance = Depends(get_existing_git_setting),
):
    return git_setting


@router.post(
    "/",
    response_model=GitInstance,
    dependencies=[
        Depends(auth_injectables.RoleVerification(required_role=Role.ADMIN))
    ],
)
def create_git_settings(
    post_git_setting: PostGitInstance,
    db: Session = Depends(get_db),
) -> DatabaseGitInstance:
    return crud.create_git_setting(db, post_git_setting)


@router.put(
    "/{git_setting_id}",
    response_model=GitInstance,
    dependencies=[
        Depends(auth_injectables.RoleVerification(required_role=Role.ADMIN))
    ],
)
def edit_git_settings(
    put_git_setting: PostGitInstance,
    db_git_setting: DatabaseGitInstance = Depends(get_existing_git_setting),
    db: Session = Depends(get_db),
) -> DatabaseGitInstance:
    return crud.update_git_setting(db, db_git_setting, put_git_setting)


@router.delete(
    "/{git_setting_id}",
    dependencies=[
        Depends(auth_injectables.RoleVerification(required_role=Role.ADMIN))
    ],
)
def delete_git_settings(
    git_setting: DatabaseGitInstance = Depends(get_existing_git_setting),
    db: Session = Depends(get_db),
):
    return crud.delete_git_setting(db, git_setting)


# In the future, check if the HTTP QUERY method is available in fast api,
# and if so, use it instead of POST
# (https://www.ietf.org/archive/id/draft-ietf-httpbis-safe-method-w-body-02.html)
@router.post("/revisions", response_model=GetRevisionsResponseModel)
def get_revisions(
    body: GetRevisionModel,
) -> GetRevisionsResponseModel:
    url = body.url
    username = body.credentials.username
    password = body.credentials.password

    return get_remote_refs(url, username, password)
