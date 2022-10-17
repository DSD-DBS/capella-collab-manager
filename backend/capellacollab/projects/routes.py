# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import importlib
import logging
import typing as t
from importlib import metadata

from fastapi import APIRouter, Depends, HTTPException
from requests import Session
from sqlalchemy.exc import IntegrityError

import capellacollab.projects.crud as crud
import capellacollab.projects.users.crud as users_crud
import capellacollab.users.crud as database_users
from capellacollab.core.authentication.database import (
    is_admin,
    verify_admin,
    verify_project_role,
)
from capellacollab.core.authentication.helper import get_username
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.authentication.responses import (
    AUTHENTICATION_RESPONSES,
)
from capellacollab.core.database import get_db
from capellacollab.projects.models import (
    DatabaseProject,
    PatchProject,
    PostProjectRequest,
    Project,
    UserMetadata,
)
from capellacollab.projects.users.models import (
    ProjectUserAssociation,
    ProjectUserPermission,
    ProjectUserRole,
)

from .capellamodels.modelsources.git.routes import router as router_sources_git
from .capellamodels.modelsources.t4c.routes import router as router_sources_t4c
from .capellamodels.routes import router as router_models
from .users.routes import router as router_users

log = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/",
    response_model=t.List[Project],
    tags=["Projects"],
    responses=AUTHENTICATION_RESPONSES,
)
def get_projects(
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
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
    tags=["Projects"],
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

    return convert_project(crud.get_project_by_name(database, project))


@router.get("/{slug}", tags=["Projects"], responses=AUTHENTICATION_RESPONSES)
def get_project_by_slug(slug: str, db: Session = Depends(get_db)):
    return convert_project(crud.get_project_by_slug(db, slug))


@router.post("/", tags=["Projects"], responses=AUTHENTICATION_RESPONSES)
def create_project(
    body: PostProjectRequest,
    db: Session = Depends(get_db),
    token: JWTBearer = Depends(JWTBearer()),
):
    try:
        project = crud.create_project(db, body.name, body.description)
    except IntegrityError as e:
        raise HTTPException(
            409,
            {
                "reason": "A project with a similar name already exists.",
                "technical": "Slug already used",
            },
        ) from e
    users_crud.add_user_to_project(
        db,
        project.name,
        ProjectUserRole.MANAGER,
        get_username(token),
        ProjectUserPermission.WRITE,
    )
    return convert_project(project)


@router.delete(
    "/{project}",
    tags=["Projects"],
    status_code=204,
    responses=AUTHENTICATION_RESPONSES,
)
def delete_project(
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
                    if user.role == ProjectUserRole.MANAGER
                ]
            ),
            contributors=len(
                [
                    user
                    for user in project.users
                    if user.role == ProjectUserRole.USER
                    and user.permission == ProjectUserPermission.WRITE
                ]
            ),
            subscribers=len(
                [
                    user
                    for user in project.users
                    if user.role == ProjectUserRole.USER
                    and user.permission == ProjectUserPermission.READ
                ]
            ),
        ),
    )


router.include_router(
    router_users, tags=["Projects"], prefix="/{project}/users"
)
router.include_router(
    router_models, tags=["Projects"], prefix="/{project_slug}/models"
)
router.include_router(
    router_sources_git,
    tags=["Projects"],
    prefix="/{project_name}/models/{model_slug}/git",
)
router.include_router(
    router_sources_t4c,
    tags=["Projects"],
    prefix="/{project_name}/models/{model_slug}/t4c",
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
