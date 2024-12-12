# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import logging

import fastapi
import slugify
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core import logging as core_logging
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.events import crud as events_crud
from capellacollab.projects import injectables as projects_injectables
from capellacollab.projects.events import routes as projects_events_routes
from capellacollab.projects.toolmodels import routes as toolmodels_routes
from capellacollab.projects.toolmodels.backups import core as backups_core
from capellacollab.projects.toolmodels.backups import crud as backups_crud
from capellacollab.projects.toolmodels.backups import models as backups_models
from capellacollab.projects.tools import routes as projects_tools_routes
from capellacollab.projects.users import crud as projects_users_crud
from capellacollab.projects.users import models as projects_users_models
from capellacollab.projects.users import routes as projects_users_routes
from capellacollab.users import injectables as users_injectables
from capellacollab.users import models as users_models

from . import crud, exceptions, models

router = fastapi.APIRouter(
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.USER
            )
        )
    ]
)


@router.get("", response_model=list[models.Project], tags=["Projects"])
def get_projects(
    minimum_role: projects_users_models.ProjectUserRole | None = None,
    user: users_models.DatabaseUser = fastapi.Depends(
        users_injectables.get_own_user
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
    log: logging.LoggerAdapter = fastapi.Depends(
        core_logging.get_request_logger
    ),
) -> list[models.DatabaseProject]:
    if user.role == users_models.Role.ADMIN:
        log.debug("Fetching all projects")
        return list(crud.get_projects(db))

    if not minimum_role:
        projects = [
            association.project
            for association in user.projects
            if not association.project.visibility
            == models.ProjectVisibility.INTERNAL
        ]
        projects.extend(crud.get_internal_projects(db))
    else:
        projects = [
            association.project
            for association in user.projects
            if auth_injectables.ProjectRoleVerification(
                minimum_role, verify=False
            )(association.project.slug, user.name, db)
        ]

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
        projects_injectables.get_existing_project
    ),
    user: users_models.DatabaseUser = fastapi.Depends(
        users_injectables.get_own_user
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.DatabaseProject:
    if patch_project.name:
        new_slug = slugify.slugify(patch_project.name)

        if project.slug != new_slug and crud.get_project_by_slug(db, new_slug):
            raise exceptions.ProjectAlreadyExistsError(project.slug)
    if patch_project.is_archived:
        _delete_all_pipelines_for_project(db, project, user)
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
        projects_injectables.get_existing_project
    ),
) -> models.DatabaseProject:
    return db_project


@router.post("", response_model=models.Project, tags=["Projects"])
def create_project(
    post_project: models.PostProjectRequest,
    user: users_models.DatabaseUser = fastapi.Depends(
        users_injectables.get_own_user
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.DatabaseProject:
    slug = slugify.slugify(post_project.name)
    if crud.get_project_by_slug(db, slug):
        raise exceptions.ProjectAlreadyExistsError(slug)

    project = crud.create_project(
        db,
        post_project.name,
        post_project.description or "",
        post_project.visibility,
        post_project.type,
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
        projects_injectables.get_existing_project
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    if project.models:
        raise exceptions.AssignedModelsPreventDeletionError(project)
    projects_users_crud.delete_users_from_project(db, project)
    events_crud.delete_all_events_projects_associated_with(db, project.id)

    crud.delete_project(db, project)


def _delete_all_pipelines_for_project(
    db: orm.Session,
    project: models.DatabaseProject,
    user: users_models.DatabaseUser,
):
    pipelines: list[backups_models.DatabaseBackup] = []
    for model in project.models:
        pipelines.extend(backups_crud.get_pipelines_for_tool_model(db, model))
    for pipeline in pipelines:
        backups_core.delete_pipeline(db, pipeline, user, True)


router.include_router(
    projects_users_routes.router,
    tags=["Projects"],
    prefix="/{project_slug}/users",
)
router.include_router(
    toolmodels_routes.router,
    prefix="/{project_slug}/models",
)
router.include_router(
    projects_events_routes.router,
    prefix="/{project_slug}/events",
    tags=["Projects - Events"],
)
router.include_router(
    projects_tools_routes.router,
    prefix="/{project_slug}/tools",
    tags=["Projects - Tools"],
)
