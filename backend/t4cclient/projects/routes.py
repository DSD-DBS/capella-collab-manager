# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

# Standard library:
import importlib
import logging
import typing as t
from importlib import metadata

# 3rd party:
from fastapi import APIRouter, Depends
from requests import Session

# local:
import t4cclient.projects.crud as crud
from .users import routes as router_users
from t4cclient.core.authentication.database import (
    is_admin,
    verify_admin,
    verify_repository_role,
)
from t4cclient.core.authentication.helper import get_username
from t4cclient.core.authentication.jwt_bearer import JWTBearer
from t4cclient.core.database import get_db
from t4cclient.core.database import users as database_users
from t4cclient.projects.models import (
    DatabaseProject,
    PostRepositoryRequest,
    Project,
    UserMetadata,
)
from t4cclient.projects.users.models import (
    ProjectUserAssociation,
    RepositoryUserPermission,
    RepositoryUserRole,
)
from t4cclient.routes.open_api_configuration import AUTHENTICATION_RESPONSES

log = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/",
    response_model=t.List[Project],
    tags=["projects"],
    responses=AUTHENTICATION_RESPONSES,
)
def get_projects(db: Session = Depends(get_db), token=Depends(JWTBearer())):
    if is_admin(token, db):
        projects = crud.get_all_projects(db)
    else:
        project_user: list[ProjectUserAssociation] = database_users.get_user(
            db=db, username=get_username(token)
        ).projects
        projects = [project.projects for project in project_user]

    return [convert_project(project) for project in projects]


@router.get("/{project}", tags=["Repositories"], responses=AUTHENTICATION_RESPONSES)
def get_repository_by_name(
    project: str, db: Session = Depends(get_db), token=Depends(JWTBearer())
):
    verify_repository_role(project, token=token, db=db)
    return convert_project(crud.get_project(db, project))


@router.post("/", tags=["Repositories"], responses=AUTHENTICATION_RESPONSES)
def create_repository(
    body: PostRepositoryRequest,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    verify_admin(token, db)
    return convert_project(crud.create_project(db, body.name))


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
    crud.delete_project(db, project)


def convert_project(project: DatabaseProject) -> Project:
    return Project(
        name=project.name,
        description=project.description,
        users=UserMetadata(
            leads=len(
                [
                    user
                    for user in project.users
                    if user.role == RepositoryUserRole.MANAGER
                ]
            ),
            contributors=len(
                [
                    user
                    for user in project.users
                    if user.role == RepositoryUserRole.USER
                    and user.permission == RepositoryUserPermission.WRITE
                ]
            ),
            subscribers=len(
                [
                    user
                    for user in project.users
                    if user.role == RepositoryUserRole.USER
                    and user.permission == RepositoryUserPermission.READ
                ]
            ),
        ),
    )


router.include_router(
    router_users.router,
    prefix="/{project}/users",
    tags=["project users"],
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
