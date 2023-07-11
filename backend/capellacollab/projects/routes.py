# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import logging
from collections import abc

import fastapi
import slugify
from fastapi import status
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core import logging as core_logging
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.core.authentication import jwt_bearer
from capellacollab.projects.toolmodels import (
    injectables as toolmodels_injectables,
)
from capellacollab.projects.toolmodels import routes as toolmodels_routes
from capellacollab.projects.users import crud as projects_users_crud
from capellacollab.projects.users import models as projects_users_models
from capellacollab.projects.users import routes as projects_users_routes
from capellacollab.sessions import routes as session_routes
from capellacollab.users import injectables as users_injectables
from capellacollab.users import models as users_models
from capellacollab.users.events import crud as events_crud

from . import crud, models

logger = logging.getLogger(__name__)
router = fastapi.APIRouter(
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.USER
            )
        )
    ]
)


@router.get(
    "/", response_model=abc.Sequence[models.Project], tags=["Projects"]
)
def get_projects(
    user: users_models.DatabaseUser = fastapi.Depends(
        users_injectables.get_own_user
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
    token=fastapi.Depends(jwt_bearer.JWTBearer()),
    log: logging.LoggerAdapter = fastapi.Depends(
        core_logging.get_request_logger
    ),
) -> abc.Sequence[models.DatabaseProject]:
    if auth_injectables.RoleVerification(
        required_role=users_models.Role.ADMIN, verify=False
    )(token, db):
        log.debug("Fetching all projects")
        return crud.get_projects(db)

    projects = [
        association.project
        for association in user.projects
        if not association.project.visibility == models.Visibility.INTERNAL
    ] + crud.get_internal_projects(db)

    log.debug("Fetching the following projects: %s", projects)
    return projects


@router.patch(
    "/{project_slug}",
    response_model=models.Project,
    tags=["Projects"],
    dependencies=[
        fastapi.Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=projects_users_models.ProjectUserRole.MANAGER
            )
        )
    ],
)
def update_project(
    patch_project: models.PatchProject,
    project: models.DatabaseProject = fastapi.Depends(
        toolmodels_injectables.get_existing_project
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.DatabaseProject:
    new_slug = slugify.slugify(patch_project.name)
    if crud.get_project_by_slug(db, new_slug) and project.slug != new_slug:
        raise fastapi.HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            details={
                "reason": "A project with a similar name already exists.",
                "technical": "Slug already used",
            },
        )
    return crud.update_project(db, project, patch_project)


@router.get(
    "/{project_slug}",
    response_model=models.Project,
    tags=["Projects"],
    dependencies=[
        fastapi.Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=projects_users_models.ProjectUserRole.USER
            )
        )
    ],
)
def get_project_by_slug(
    db_project: models.DatabaseProject = fastapi.Depends(
        toolmodels_injectables.get_existing_project
    ),
) -> models.DatabaseProject:
    return db_project


@router.post("/", response_model=models.Project, tags=["Projects"])
def create_project(
    post_project: models.PostProjectRequest,
    user: users_models.DatabaseUser = fastapi.Depends(
        users_injectables.get_own_user
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.DatabaseProject:
    if crud.get_project_by_slug(db, slugify.slugify(post_project.name)):
        raise fastapi.HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "reason": "A project with a similar name already exists.",
                "technical": "Slug already used",
            },
        )

    project = crud.create_project(
        db,
        post_project.name,
        post_project.description,
        post_project.visibility,
    )

    if user.role != users_models.Role.ADMIN:
        projects_users_crud.add_user_to_project(
            db,
            project,
            user,
            projects_users_models.ProjectUserRole.MANAGER,
            projects_users_models.ProjectUserPermission.WRITE,
        )

    return project


@router.delete(
    "/{project_slug}",
    tags=["Projects"],
    status_code=204,
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.ADMIN
            )
        )
    ],
)
def delete_project(
    project: models.DatabaseProject = fastapi.Depends(
        toolmodels_injectables.get_existing_project
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    if project.models:
        raise fastapi.HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"reason": "The project still has models assigned to it"},
        )
    projects_users_crud.delete_users_from_project(db, project)
    events_crud.delete_all_events_projects_associated_with(db, project.id)

    crud.delete_project(db, project)


router.include_router(
    projects_users_routes.router,
    tags=["Projects"],
    prefix="/{project_slug}/users",
)
router.include_router(
    toolmodels_routes.router,
    prefix="/{project_slug}/models",
    tags=["Projects - Models"],
)
router.include_router(
    session_routes.project_router,
    prefix="/{project_slug}/sessions",
    tags=["Projects - Sessions"],
)
