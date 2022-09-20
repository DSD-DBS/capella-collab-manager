# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import importlib
import logging
import typing as t
from importlib import metadata

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session

import capellacollab.projects.crud as crud
import capellacollab.projects.users.crud as users_crud
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
from capellacollab.core.database import users as database_users
from capellacollab.projects.models import (
    DatabaseProject,
    PatchProject,
    PostRepositoryRequest,
    Project,
    UserMetadata,
)
from capellacollab.projects.users import crud as repository_users
from capellacollab.projects.users.models import (
    ProjectUserAssociation,
    RepositoryUserPermission,
    RepositoryUserRole,
)
from capellacollab.sql_models.users import DatabaseUser

from .capellamodels.routes import router as router_models
from .users.routes import router as router_users

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


@router.get(
    "/{project}", tags=["Repositories"], responses=AUTHENTICATION_RESPONSES
)
def get_repository_by_name(project: str, db: Session = Depends(get_db)):
    return convert_project(crud.get_project(db, project))


@router.get("/details/", response_model=Project)
def get_project(
    slug: str,
    db: Session = Depends(get_db),
) -> Project:
    project = crud.get_project_by_slug(db, slug)
    return convert_project(project)


@router.post("/", tags=["Repositories"], responses=AUTHENTICATION_RESPONSES)
def create_repository(
    body: PostRepositoryRequest,
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
    users_crud.add_user_to_repository(
        db,
        project.name,
        RepositoryUserRole.MANAGER,
        get_username(token),
        RepositoryUserPermission.WRITE,
    )
    return convert_project(project)


@router.delete(
    "/{project_slug}",
    tags=["Repositories"],
    status_code=204,
    responses=AUTHENTICATION_RESPONSES,
)
def delete_project(
    project_slug: str,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
) -> None:
    verify_admin(token, db)
    project = crud.get_project_by_slug(db, project_slug)
    staged_by = project.staged_by
    if not staged_by:
        raise HTTPException(
            status_code=409,
            detail={
                "err_code": "unstaged_project",
                "reason": "The repository has to be staged by another administrator before deletion.",
            },
        )
    if staged_by.name == get_username(token):
        raise HTTPException(
            status_code=409,
            detail={
                "err_code": "not_staged_and_deleted",
                "reason": "A single administrator can not stage and delete a repository at the same time.",
            },
        )
    db.delete(project)
    db.commit()


@router.patch(
    "/{project_slug}/stage",
    tags=["Repositories"],
    status_code=204,
    responses=AUTHENTICATION_RESPONSES,
)
def stage_project(
    project_slug: str,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
) -> Project:
    project = crud.get_project_by_slug(db, project_slug)
    verify_project_role(
        project.name, token, db, allowed_roles=["administrator", "manager"]
    )
    check_repository_exists(project.name, db)
    username = get_username(token)
    user = db.execute(
        select(DatabaseUser).filter_by(name=username)
    ).scalar_one()
    project.staged_by = user
    db.commit()
    return Project.from_orm(project)


@router.patch("/{project_slug}/unstage")
def unstage_project(
    project_slug: str,
    db: Session = Depends(get_db),
    token: JWTBearer = Depends(JWTBearer()),
) -> Project:
    project = crud.get_project_by_slug(db, project_slug)
    if not project:
        raise HTTPException(404, "Project not found")
    verify_project_role(
        project.name, token, db, allowed_roles=["administrator", "manager"]
    )
    return Project.from_orm(repository_users.unstage_project(db, project))


def check_repository_exists(
    project_name: str,
    db: Session,
) -> DatabaseProject:
    project = crud.get_project(db, project_name)
    if not project:
        raise HTTPException(
            status_code=404,
            detail={
                "err_code": "project_does_not_exist",
                "reason": "The project does not exist.",
            },
        )
    return project


def convert_project(db_project: DatabaseProject) -> Project:
    project = Project.from_orm(db_project)
    project.users_metadata = UserMetadata(
        leads=len(
            [
                user
                for user in db_project.users
                if user.role == RepositoryUserRole.MANAGER
            ]
        ),
        contributors=len(
            [
                user
                for user in db_project.users
                if user.role == RepositoryUserRole.USER
                and user.permission == RepositoryUserPermission.WRITE
            ]
        ),
        subscribers=len(
            [
                user
                for user in db_project.users
                if user.role == RepositoryUserRole.USER
                and user.permission == RepositoryUserPermission.READ
            ]
        ),
    )
    return project


router.include_router(router_users, prefix="/{project}/users")
router.include_router(router_models, prefix="/{project_slug}/models")

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
