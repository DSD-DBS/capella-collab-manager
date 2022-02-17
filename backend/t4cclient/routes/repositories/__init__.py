import typing as t

import t4cclient.core.services.repositories as repository_service
from fastapi import APIRouter, Depends
from requests import Session
from t4cclient.config import USERNAME_CLAIM
from t4cclient.core.database import get_db, repositories
from t4cclient.core.database import users as database_users
from t4cclient.core.oauth.database import is_admin, verify_admin, verify_repository_role
from t4cclient.core.oauth.jwt_bearer import JWTBearer
from t4cclient.extensions import t4c
from t4cclient.routes.open_api_configuration import AUTHENTICATION_RESPONSES
from t4cclient.schemas.repositories import (
    GetRepositoryUserResponse,
    PostRepositoryRequest,
    RepositoryUserPermission,
    RepositoryUserRole,
)

from . import git_models as router_git_models
from . import projects as router_projects
from . import users as router_users

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

    db_user = database_users.get_user(db=db, username=token[USERNAME_CLAIM])
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


@router.get(
    "/{repository_name}", tags=["Repositories"], responses=AUTHENTICATION_RESPONSES
)
def get_repository_by_name(
    repository_name: str, db: Session = Depends(get_db), token=Depends(JWTBearer())
):
    verify_repository_role(repository_name, token=token, db=db)
    return repositories.get_repository(db, repository_name)


@router.post("/", tags=["Repositories"], responses=AUTHENTICATION_RESPONSES)
def create_repository(
    body: PostRepositoryRequest,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    verify_admin(token, db)
    t4c.create_repository(body.name)
    return repositories.create_repository(db, body.name)


@router.delete(
    "/{repository_name}",
    tags=["Repositories"],
    status_code=204,
    responses=AUTHENTICATION_RESPONSES,
)
def delete_repository(
    repository_name: str, db: Session = Depends(get_db), token=Depends(JWTBearer())
):
    verify_admin(token, db)
    repositories.delete_repository(db, repository_name)


router.include_router(
    router_users.router,
    prefix="/{repository_name}/users",
    tags=["Repository Users"],
)
router.include_router(
    router_git_models.router,
    prefix="/{repository_name}/git-models",
    tags=["Repository Git Models"],
)
router.include_router(
    router_projects.router,
    prefix="/{repository_name}/projects",
    tags=["Repository Projects"],
)
