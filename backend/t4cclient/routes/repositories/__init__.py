# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import importlib
import logging
import typing as t
from importlib import metadata

import t4cclient.core.services.repositories as repository_service
import t4cclient.schemas.repositories as schema_repositories
from fastapi import APIRouter, Depends
from requests import Session
from t4cclient.core.authentication.database import (
    check_repository_exists, is_admin, verify_admin,
    verify_not_staged_and_deleted, verify_repository_role, verify_staged)
from t4cclient.core.authentication.helper import get_username
from t4cclient.core.authentication.jwt_bearer import JWTBearer
from t4cclient.core.database import get_db, repositories, repository_users
from t4cclient.core.database import users as database_users
from t4cclient.extensions.modelsources.t4c import connection
from t4cclient.routes.open_api_configuration import AUTHENTICATION_RESPONSES
from t4cclient.schemas.repositories import (GetRepositoryUserResponse,
                                            PostRepositoryRequest,
                                            RepositoryUserPermission,
                                            RepositoryUserRole)

from . import users as router_users

log = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/",
    response_model=t.List[GetRepositoryUserResponse],
    tags=["Repositories"],
    responses=AUTHENTICATION_RESPONSES,
)
def get_repositories(db: Session = Depends(get_db), token=Depends(JWTBearer())):
    if is_admin(token, db):
        return [
            GetRepositoryUserResponse(
                repository_name=repo.name,
                permissions=repository_service.get_permission(
                    RepositoryUserPermission.WRITE, repo.name, db
                ),
                staged_by=repo.staged_by,
                warnings=repository_service.get_warnings(repo.name, db),
                role=RepositoryUserRole.ADMIN,
            )
            for repo in repositories.get_all_repositories(db)
        ]

    db_user = database_users.get_user(db=db, username=get_username(token))
    return [
        GetRepositoryUserResponse(
            repository_name=repo.repository_name,
            role=repo.role,
            staged_by=repo.repository.staged_by,
            permissions=repository_service.get_permission(
                repo.permission, repo.repository_name, db
            ),
            warnings=repository_service.get_warnings(repo.repository_name, db),
        )
        for repo in db_user.repositories
    ]


@router.get("/{project}", tags=["Repositories"], responses=AUTHENTICATION_RESPONSES)
def get_repository_by_name(
    project: str, db: Session = Depends(get_db), token=Depends(JWTBearer())
):
    verify_repository_role(project, token=token, db=db)
    return repositories.get_repository(db, project)


@router.post("/", tags=["Repositories"], responses=AUTHENTICATION_RESPONSES)
def create_repository(
    body: PostRepositoryRequest,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    verify_admin(token, db)
    connection.create_repository(body.name)
    return repositories.create_repository(db, body.name)


@router.delete(
    "/{project}",
    tags=["Repositories"],
    status_code=204,
    responses=AUTHENTICATION_RESPONSES,
)
def delete_repository(
    project: str, db: Session = Depends(get_db), token=Depends(JWTBearer())
):
    verify_admin(token, db)
    verify_staged(project, db)
    verify_not_staged_and_deleted(project, get_username(token), db)
    check_repository_exists(project, db)
    for user in repository_users.get_users_of_repository(db, project):
        repository_users.delete_user_from_repository(db, project, user.username)
    repositories.delete_repository(db, project)


@router.patch(
    "/{project}",
    tags=["Repositories"],
    status_code=204,
    responses=AUTHENTICATION_RESPONSES,
)
def stage_for_deletion_repository(
    project: str,
    body: schema_repositories.StageRepositoryRequest,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    verify_repository_role(
        repository=project,
        token=token,
        db=db,
        allowed_roles=["manager", "administrator"],
    )
    repositories.stage_repository_for_deletion(db, project, body.username)
    repository_users.stage_repository(db, project, body.username)


router.include_router(
    router_users.router,
    prefix="/{project}/users",
    tags=["Repository Users"],
)

# Load backup extension routes
eps = metadata.entry_points()["capellacollab.extensions.backups"]
for ep in eps:
    log.info("Add routes of backup extension %s", ep.name)
    router.include_router(
        importlib.import_module(".routes", ep.module).router,
        prefix="/{project}/extensions/backups/" + ep.name,
        tags=[ep.name],
    )

# Load modelsource extension routes
eps = metadata.entry_points()["capellacollab.extensions.modelsources"]
for ep in eps:
    log.info("Add routes of modelsource %s", ep.name)
    router.include_router(
        importlib.import_module(".routes", ep.module).router,
        prefix="/{project}/extensions/modelsources/" + ep.name,
        tags=[ep.name],
    )
