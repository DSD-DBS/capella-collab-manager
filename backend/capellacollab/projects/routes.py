# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

# Standard library:
import importlib
import json
import logging
import typing as t
from importlib import metadata

# 3rd party:
from fastapi import APIRouter, Depends
from requests import Session

# 1st party:
import capellacollab.projects.crud as crud

# local:
from .users.routes import router as router_users
from capellacollab.core.authentication.database import (
    is_admin,
    verify_admin,
    verify_project_role,
)
from capellacollab.core.authentication.helper import get_username
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.database import get_db
from capellacollab.core.database import users as database_users
from capellacollab.projects.models import (
    DatabaseProject,
    PatchProject,
    PostRepositoryRequest,
    Project,
    UserMetadata,
)
from capellacollab.projects.users.models import (
    ProjectUserAssociation,
    RepositoryUserPermission,
    RepositoryUserRole,
)
from capellacollab.routes.open_api_configuration import AUTHENTICATION_RESPONSES

log = logging.getLogger(__name__)
router = APIRouter()

router.include_router(router_users, prefix="/{project}/users")


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


@router.patch(
    "/{project}",
    response_model=Project,
    tags=["projects"],
    responses=AUTHENTICATION_RESPONSES,
)
def update_project(
    project: str,
    body: PatchProject,
    database: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):

    log.info(
        "User %s updated the description of project %s to '%s'",
        get_username(token),
        project,
        body.description,
    )

    verify_project_role(project, token, database, ["manager", "administrator"])

    crud.update_description(database, project, body.description)

    return convert_project(crud.get_project(database, project))


@router.get("/{project}", tags=["Repositories"], responses=AUTHENTICATION_RESPONSES)
def get_repository_by_name(project: str, db: Session = Depends(get_db)):
    return convert_project(crud.get_project(db, project))


@router.get("/details/", response_model=Project)
def get(
    slug: str,
    db: Session = Depends(get_db),
):
    project = crud.get_project_by_slug(db, slug)
    return convert_project(project)


@router.post("/", tags=["Repositories"], responses=AUTHENTICATION_RESPONSES)
def create_repository(
    body: PostRepositoryRequest,
    db: Session = Depends(get_db),
    token: JWTBearer = Depends(JWTBearer()),
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
        slug=project.slug,
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
