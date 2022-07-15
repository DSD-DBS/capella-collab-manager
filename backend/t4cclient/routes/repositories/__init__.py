# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import importlib
import logging
import typing as t
from importlib import metadata

from fastapi import APIRouter, Depends
from requests import Session

import t4cclient.core.services.repositories as repository_service
from . import users as router_users
from t4cclient.core.authentication.database import (
    is_admin,
    verify_admin,
    verify_repository_role,
)
from t4cclient.core.authentication.helper import get_username
from t4cclient.core.authentication.jwt_bearer import JWTBearer
from t4cclient.core.database import get_db, repositories
from t4cclient.core.database import users as database_users
from t4cclient.core.oauth.responses import AUTHENTICATION_RESPONSES
from t4cclient.extensions.modelsources.t4c import connection
from t4cclient.schemas.repositories import (
    GetRepositoryUserResponse,
    PostRepositoryRequest,
    RepositoryUserPermission,
    RepositoryUserRole,
)

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
    connection.add_user_to_repository(body.name, get_username(token), is_admin=True)
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
    repositories.delete_repository(db, project)


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
