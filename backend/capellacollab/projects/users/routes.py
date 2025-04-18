# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

import fastapi
import pydantic
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.events import crud as events_crud
from capellacollab.events import models as events_models
from capellacollab.permissions import models as permissions_models
from capellacollab.projects import injectables as projects_injectables
from capellacollab.projects import models as projects_models
from capellacollab.projects.permissions import (
    injectables as projects_permissions_injectables,
)
from capellacollab.projects.permissions import (
    models as projects_permissions_models,
)
from capellacollab.projects.permissions import (
    routes as projects_permissions_routes,
)
from capellacollab.users import crud as users_crud
from capellacollab.users import exceptions as users_exceptions
from capellacollab.users import injectables as users_injectables
from capellacollab.users import models as users_models

from . import crud, exceptions, models, util

router = fastapi.APIRouter()


def check_user_not_in_project(
    project: projects_models.DatabaseProject, user: users_models.DatabaseUser
):
    if user in [user.user for user in project.users]:
        raise exceptions.ProjectUserAlreadyExistsError(user.name, project.slug)


def get_project_user_association_or_raise(
    db: orm.Session,
    project: projects_models.DatabaseProject,
    user: users_models.DatabaseUser,
) -> models.DatabaseProjectUserAssociation | models.ProjectUser:
    if project_user := crud.get_project_user_association(db, project, user):
        return project_user

    if project.visibility == projects_models.ProjectVisibility.INTERNAL:
        return models.ProjectUser(
            role=models.ProjectUserRole.USER,
            permission=models.ProjectUserPermission.READ,
            user=users_models.User.model_validate(user),
        )

    raise exceptions.ProjectUserNotFoundError(
        username=user.name, project_slug=project.slug
    )


@router.get("/current", response_model=models.ProjectUser)
def get_current_project_user(
    user: t.Annotated[
        users_models.DatabaseUser,
        fastapi.Depends(users_injectables.get_own_user),
    ],
    project: t.Annotated[
        projects_models.DatabaseProject,
        fastapi.Depends(projects_injectables.get_existing_project),
    ],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
) -> models.DatabaseProjectUserAssociation | models.ProjectUser:
    """Get the current project users"""
    if user.role == users_models.Role.ADMIN:
        return models.ProjectUser(
            role=models.ProjectUserRole.ADMIN,
            permission=models.ProjectUserPermission.WRITE,
            user=users_models.User.model_validate(user),
        )
    return get_project_user_association_or_raise(db, project, user)


@router.get(
    "",
    response_model=list[models.ProjectUser],
    dependencies=[
        fastapi.Depends(
            projects_permissions_injectables.ProjectPermissionValidation(
                required_scope=projects_permissions_models.ProjectUserScopes(
                    project_users={permissions_models.UserTokenVerb.GET}
                )
            )
        )
    ],
)
def get_users_for_project(
    project: t.Annotated[
        projects_models.DatabaseProject,
        fastapi.Depends(projects_injectables.get_existing_project),
    ],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
) -> list[models.ProjectUser]:
    return pydantic.TypeAdapter(list[models.ProjectUser]).validate_python(
        project.users
    ) + [
        models.ProjectUser(
            role=models.ProjectUserRole.ADMIN,
            permission=models.ProjectUserPermission.WRITE,
            user=users_models.User.model_validate(user),
        )
        for user in users_crud.get_admin_users(db)
    ]


@router.post(
    "",
    response_model=models.ProjectUser,
    dependencies=[
        fastapi.Depends(
            projects_permissions_injectables.ProjectPermissionValidation(
                required_scope=projects_permissions_models.ProjectUserScopes(
                    project_users={permissions_models.UserTokenVerb.CREATE}
                )
            )
        )
    ],
)
def add_user_to_project(
    post_project_user: models.PostProjectUser,
    project: t.Annotated[
        projects_models.DatabaseProject,
        fastapi.Depends(projects_injectables.get_existing_project),
    ],
    own_user: t.Annotated[
        users_models.DatabaseUser,
        fastapi.Depends(users_injectables.get_own_user),
    ],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
) -> models.DatabaseProjectUserAssociation:
    if not (
        user := users_crud.get_user_by_name(db, post_project_user.username)
    ):
        raise users_exceptions.UserNotFoundError(
            username=post_project_user.username
        )
    check_user_not_in_project(project, user)

    if post_project_user.role == models.ProjectUserRole.MANAGER:
        post_project_user.permission = models.ProjectUserPermission.WRITE

    association = crud.add_user_to_project(
        db, project, user, post_project_user.role, post_project_user.permission
    )
    util.create_add_user_to_project_events(
        post_project_user, user, project, own_user, db
    )

    return association


@router.patch(
    "/{user_id}",
    status_code=204,
    dependencies=[
        fastapi.Depends(
            projects_permissions_injectables.ProjectPermissionValidation(
                required_scope=projects_permissions_models.ProjectUserScopes(
                    project_users={permissions_models.UserTokenVerb.UPDATE}
                )
            )
        )
    ],
)
def update_project_user(
    patch_project_user: models.PatchProjectUser,
    user: t.Annotated[
        users_models.DatabaseUser,
        fastapi.Depends(users_injectables.get_existing_user),
    ],
    project: t.Annotated[
        projects_models.DatabaseProject,
        fastapi.Depends(projects_injectables.get_existing_project),
    ],
    own_user: t.Annotated[
        users_models.DatabaseUser,
        fastapi.Depends(users_injectables.get_own_user),
    ],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
):
    if role := patch_project_user.role:
        crud.change_role_of_user_in_project(db, project, user, role)

        events_crud.create_project_change_event(
            db=db,
            user=user,
            event_type=util.get_project_role_event_type(role),
            executor=own_user,
            project=project,
            reason=patch_project_user.reason,
        )

        if role == models.ProjectUserRole.MANAGER:
            crud.change_permission_of_user_in_project(
                db, project, user, models.ProjectUserPermission.WRITE
            )

    if permission := patch_project_user.permission:
        project_user = get_project_user_association_or_raise(db, project, user)

        if project_user.role == models.ProjectUserRole.MANAGER:
            raise exceptions.PermissionForProjectLeadsNotAllowedError()
        crud.change_permission_of_user_in_project(
            db, project, user, permission
        )

        events_crud.create_project_change_event(
            db=db,
            user=user,
            event_type=util.get_project_permission_event_type(permission),
            executor=own_user,
            project=project,
            reason=patch_project_user.reason,
        )


@router.delete(
    "/{user_id}",
    status_code=204,
    dependencies=[
        fastapi.Depends(
            projects_permissions_injectables.ProjectPermissionValidation(
                required_scope=projects_permissions_models.ProjectUserScopes(
                    project_users={permissions_models.UserTokenVerb.DELETE}
                )
            )
        )
    ],
)
def remove_user_from_project(
    reason: t.Annotated[str, fastapi.Body(media_type="text/plain")],
    project: t.Annotated[
        projects_models.DatabaseProject,
        fastapi.Depends(projects_injectables.get_existing_project),
    ],
    user: t.Annotated[
        users_models.DatabaseUser,
        fastapi.Depends(users_injectables.get_existing_user),
    ],
    own_user: t.Annotated[
        users_models.DatabaseUser,
        fastapi.Depends(users_injectables.get_own_user),
    ],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
):
    crud.delete_user_from_project(db, project, user)
    events_crud.create_project_change_event(
        db,
        user,
        events_models.EventType.REMOVED_FROM_PROJECT,
        own_user,
        project,
        reason,
    )


router.include_router(
    projects_permissions_routes.users_router,
    prefix="/{user_id}/permissions",
)
