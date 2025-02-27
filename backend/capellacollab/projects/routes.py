# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import typing as t

import fastapi
import slugify
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.events import crud as events_crud
from capellacollab.permissions import injectables as permissions_injectables
from capellacollab.permissions import models as permissions_models
from capellacollab.projects import injectables as projects_injectables
from capellacollab.projects.events import routes as projects_events_routes
from capellacollab.projects.permissions import (
    injectables as projects_permissions_injectables,
)
from capellacollab.projects.permissions import (
    models as projects_permissions_models,
)
from capellacollab.projects.permissions import (
    routes as projects_permissions_routes,
)
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
from capellacollab.users.tokens import models as tokens_models

from . import crud, exceptions, models

router = fastapi.APIRouter()


@router.get(
    "",
    response_model=list[models.Project],
    tags=["Projects"],
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(required_scope=None)
        )
    ],
)
def get_projects(
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
    global_scope: t.Annotated[
        permissions_models.GlobalScopes,
        fastapi.Depends(permissions_injectables.get_scope),
    ],
    authentication_information: t.Annotated[
        tuple[
            users_models.DatabaseUser, tokens_models.DatabaseUserToken | None
        ],
        fastapi.Depends(
            auth_injectables.authentication_information_validation
        ),
    ],
    minimum_role: projects_users_models.ProjectUserRole | None = None,
) -> list[models.DatabaseProject]:
    """List all projects the user has access to.

    Internal projects are visible to all users. With the `minimum_role` query parameter,
    only projects where the user has at least the specified role are returned.
    """
    projects = []

    for project in crud.get_projects(db):
        project_scope = projects_permissions_injectables.get_scope(
            authentication_information, global_scope, project, db
        )

        if permissions_models.UserTokenVerb.GET in project_scope.root:
            if minimum_role in (
                projects_users_models.ProjectUserRole.ADMIN,
                projects_users_models.ProjectUserRole.MANAGER,
            ):
                # This is a workaround for backwards compatibility, but without dependency
                # to the removed ProjectRoleVerification
                # (project_scope.root, UPDATE) is only available admins & project leads

                if (
                    permissions_models.UserTokenVerb.UPDATE
                    in project_scope.root
                ):
                    projects.append(project)
            else:
                projects.append(project)

    return projects


@router.patch(
    "/{project_slug}",
    response_model=models.Project,
    tags=["Projects"],
    dependencies=[
        fastapi.Depends(
            projects_permissions_injectables.ProjectPermissionValidation(
                required_scope=projects_permissions_models.ProjectUserScopes(
                    root={permissions_models.UserTokenVerb.UPDATE}
                )
            )
        )
    ],
)
def update_project(
    patch_project: models.PatchProject,
    project: t.Annotated[
        models.DatabaseProject,
        fastapi.Depends(projects_injectables.get_existing_project),
    ],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
    global_scope: t.Annotated[
        permissions_models.GlobalScopes,
        fastapi.Depends(permissions_injectables.get_scope),
    ],
) -> models.DatabaseProject:
    """Update a project's metadata.

    An update of the name will also change the slug. This will break existing API routes
    and the project provisioning. Be careful with project renames.

    If the project is archived, all pipelines will be deleted.
    """
    if patch_project.name:
        new_slug = slugify.slugify(patch_project.name)

        if project.slug != new_slug and crud.get_project_by_slug(db, new_slug):
            raise exceptions.ProjectAlreadyExistsError(project.slug)
    if patch_project.is_archived:
        _delete_all_pipelines_for_project(db, project, global_scope)
    return crud.update_project(db, project, patch_project)


@router.get(
    "/{project_slug}",
    response_model=models.Project,
    tags=["Projects"],
    dependencies=[
        fastapi.Depends(
            projects_permissions_injectables.ProjectPermissionValidation(
                required_scope=projects_permissions_models.ProjectUserScopes(
                    root={permissions_models.UserTokenVerb.GET}
                )
            )
        )
    ],
)
def get_project_by_slug(
    db_project: t.Annotated[
        models.DatabaseProject,
        fastapi.Depends(projects_injectables.get_existing_project),
    ],
) -> models.DatabaseProject:
    """Get a project by its slug."""
    return db_project


@router.post(
    "",
    response_model=models.Project,
    tags=["Projects"],
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    user=permissions_models.UserScopes(
                        projects={permissions_models.UserTokenVerb.CREATE}
                    )
                )
            )
        )
    ],
)
def create_project(
    post_project: models.PostProjectRequest,
    user: t.Annotated[
        users_models.DatabaseUser,
        fastapi.Depends(users_injectables.get_own_user),
    ],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
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
            projects_permissions_injectables.ProjectPermissionValidation(
                required_scope=projects_permissions_models.ProjectUserScopes(
                    root={permissions_models.UserTokenVerb.DELETE}
                )
            )
        )
    ],
)
def delete_project(
    project: t.Annotated[
        models.DatabaseProject,
        fastapi.Depends(projects_injectables.get_existing_project),
    ],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
):
    """Delete a project.

    To avoid accidental deletions of projects, all models have to be deleted before
    removing the project.
    """
    if project.models:
        raise exceptions.AssignedModelsPreventDeletionError(project)
    projects_users_crud.delete_users_from_project(db, project)
    events_crud.delete_all_events_projects_associated_with(db, project.id)

    crud.delete_project(db, project)


def _delete_all_pipelines_for_project(
    db: orm.Session,
    project: models.DatabaseProject,
    global_scope: permissions_models.GlobalScopes,
):
    pipelines: list[backups_models.DatabaseBackup] = []
    for model in project.models:
        pipelines.extend(backups_crud.get_pipelines_for_tool_model(db, model))
    for pipeline in pipelines:
        backups_core.delete_pipeline(db, pipeline, True, global_scope)


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
router.include_router(
    projects_permissions_routes.router,
    prefix="/-/permissions",
    tags=["Projects - Permissions"],
)
