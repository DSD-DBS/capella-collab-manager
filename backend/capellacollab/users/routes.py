# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t
from collections import abc

import fastapi
from sqlalchemy import orm

from capellacollab.configuration import core as config_core
from capellacollab.core import database
from capellacollab.events import crud as events_crud
from capellacollab.events import models as events_models
from capellacollab.feedback import crud as feedback_crud
from capellacollab.permissions import injectables as permissions_injectables
from capellacollab.permissions import models as permissions_models
from capellacollab.permissions import routes as permissions_routes
from capellacollab.projects import crud as projects_crud
from capellacollab.projects import models as projects_models
from capellacollab.projects.users import crud as projects_users_crud
from capellacollab.sessions import routes as session_routes
from capellacollab.tags import core as tags_core
from capellacollab.tags import models as tags_models
from capellacollab.users import injectables as users_injectables
from capellacollab.users.tokens import routes as tokens_routes
from capellacollab.users.workspaces import routes as workspaces_routes
from capellacollab.users.workspaces import util as workspaces_util

from . import crud, exceptions, injectables, models

router = fastapi.APIRouter()


@router.get("/current", response_model=models.User, tags=["Users"])
def get_current_user(
    user: t.Annotated[
        models.DatabaseUser, fastapi.Depends(injectables.get_own_user)
    ],
) -> models.DatabaseUser:
    """Return the user that is currently logged in. No specific permissions required."""
    return user


@router.get("/{user_id}", response_model=models.User, tags=["Users"])
def get_user(
    own_user: t.Annotated[
        models.DatabaseUser, fastapi.Depends(injectables.get_own_user)
    ],
    user: t.Annotated[
        models.DatabaseUser, fastapi.Depends(injectables.get_existing_user)
    ],
    scope: t.Annotated[
        permissions_models.GlobalScopes,
        fastapi.Depends(permissions_injectables.get_scope),
    ],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
) -> models.DatabaseUser:
    """Return the user.

    Requires scope `admin.users:get` or at least one common project with the user.
    """
    if (
        user.id == own_user.id
        or len(projects_crud.get_common_projects_for_users(db, own_user, user))
        > 0
        or permissions_models.UserTokenVerb.GET in scope.admin.users
    ):
        return user
    raise exceptions.NoProjectsInCommonError(user.id)


@router.get(
    "",
    response_model=list[models.User],
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        users={permissions_models.UserTokenVerb.GET}
                    )
                )
            )
        )
    ],
    tags=["Users"],
)
def get_users(
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
) -> abc.Sequence[models.DatabaseUser]:
    """Get all users."""
    return crud.get_users(db)


@router.post(
    "",
    response_model=models.User,
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        users={permissions_models.UserTokenVerb.CREATE}
                    )
                )
            )
        )
    ],
    tags=["Users"],
)
def create_user(
    post_user: models.PostUser,
    own_user: t.Annotated[
        models.DatabaseUser, fastapi.Depends(injectables.get_own_user)
    ],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
):
    """Create a user.

    This is usually not needed since users are auto-created on login.
    """
    created_user = crud.create_user(
        db, post_user.name, post_user.idp_identifier, post_user.email
    )
    events_crud.create_user_creation_event(
        db=db, user=created_user, executor=own_user, reason=post_user.reason
    )
    return created_user


@router.get(
    "/{user_id}/common-projects",
    response_model=list[projects_models.Project],
    tags=["Users"],
)
def get_common_projects(
    user_for_common_projects: t.Annotated[
        models.DatabaseUser, fastapi.Depends(injectables.get_existing_user)
    ],
    user: t.Annotated[
        models.DatabaseUser, fastapi.Depends(injectables.get_own_user)
    ],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
    scope: t.Annotated[
        permissions_models.GlobalScopes,
        fastapi.Depends(permissions_injectables.get_scope),
    ],
) -> list[projects_models.DatabaseProject]:
    """List all common projects with a user.

    If the user sending the request has the `admin.projects:get` and `admin.users:get` permissions,
    the API will return all projects of the selected user.
    """
    if (
        permissions_models.UserTokenVerb.GET in scope.admin.projects
        and permissions_models.UserTokenVerb.GET in scope.admin.users
    ):
        return [
            association.project
            for association in user_for_common_projects.projects
        ]
    projects = projects_crud.get_common_projects_for_users(
        db, user, user_for_common_projects
    )
    return list(projects)


@router.patch("/{user_id}", response_model=models.User, tags=["Users"])
def update_user(
    patch_user: models.PatchUser,
    user: t.Annotated[
        models.DatabaseUser, fastapi.Depends(injectables.get_existing_user)
    ],
    own_user: t.Annotated[
        models.DatabaseUser, fastapi.Depends(injectables.get_own_user)
    ],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
    scope: t.Annotated[
        permissions_models.GlobalScopes,
        fastapi.Depends(permissions_injectables.get_scope),
    ],
):
    """Update the user.

    The `reason` field is required when updating the `role` or `blocked` fields.

    The `beta_user` field can only be updated when `beta.enabled` is activated in the
    global configuration.

    The `beta_user` field can be updated for the own user when `beta.allow_self_enrollment`
    is activated in the global configuration.
    All other fields can only be updated with the `admin.users:update` scope.
    """

    # Users are only allowed to update their beta_tester status unless they have the `admin.users:update` scope
    if permissions_models.UserTokenVerb.UPDATE not in scope.admin.users:
        if own_user.id != user.id:
            raise exceptions.ChangesNotAllowedForOtherUsersError()
        if any(patch_user.model_dump(exclude={"beta_tester"}).values()):
            raise exceptions.ChangesNotAllowedForRoleError()

    if patch_user.beta_tester:
        cfg = config_core.get_global_configuration(db)
        if not cfg.beta.enabled:
            raise exceptions.BetaTestingDisabledError()
        if (
            not cfg.beta.allow_self_enrollment
            and permissions_models.UserTokenVerb.UPDATE
            not in scope.admin.users
        ):
            raise exceptions.BetaTestingSelfEnrollmentNotAllowedError()

    if patch_user.role and patch_user.role != user.role:
        if reason := patch_user.reason:
            user = update_user_role(
                db, user, own_user, patch_user.role, reason
            )
        else:
            raise exceptions.ReasonRequiredError()

    tags = tags_core.resolve_tags(
        db, patch_user.tags, tags_models.TagScope.USER
    )

    if patch_user.blocked is not None and patch_user.blocked != user.blocked:
        update_user_blocked_status(
            db, user, own_user, patch_user.blocked, patch_user.reason
        )
    patch_user.tags = None
    return crud.update_user(db, user, patch_user, tags)


def update_user_blocked_status(
    db: orm.Session,
    user: models.DatabaseUser,
    own_user: models.DatabaseUser,
    blocked: bool,
    reason: str | None,
):
    if not reason:
        raise exceptions.ReasonRequiredError()
    events_crud.create_event(
        db,
        user,
        event_type=events_models.EventType.BLOCKED_USER
        if blocked
        else events_models.EventType.UNBLOCKED_USER,
        reason=reason,
        executor=own_user,
    )


@router.delete(
    "/{user_id}",
    status_code=204,
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        users={permissions_models.UserTokenVerb.DELETE}
                    )
                )
            )
        )
    ],
    tags=["Users"],
)
def delete_user(
    user: t.Annotated[
        models.DatabaseUser, fastapi.Depends(injectables.get_existing_user)
    ],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
):
    """Delete a user irrevocably.

    The user will be removed from all projects, all events the user was involved in will be deleted,
    all workspaces of the user will be deleted, and all feedback of the user will be anonymized.
    """
    projects_users_crud.delete_projects_for_user(db, user.id)
    events_crud.delete_all_events_user_involved_in(db, user.id)
    workspaces_util.delete_all_workspaces_of_user(db, user)
    feedback_crud.anonymize_feedback_of_user(db, user)
    crud.delete_user(db, user)


@router.get(
    "/{user_id}/events",
    response_model=list[events_models.HistoryEvent],
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        users={permissions_models.UserTokenVerb.GET},
                        events={permissions_models.UserTokenVerb.GET},
                    )
                )
            )
        )
    ],
    tags=["Users"],
)
def get_user_events(
    user: t.Annotated[
        models.DatabaseUser,
        fastapi.Depends(users_injectables.get_existing_user),
    ],
) -> list[events_models.DatabaseUserHistoryEvent]:
    """List all events for the user."""
    return user.events


def update_user_role(
    db: orm.Session,
    user: models.DatabaseUser,
    executor: models.DatabaseUser,
    role: models.Role,
    reason: str,
):
    updated_user = crud.update_role_of_user(db, user, role)

    event_type = (
        events_models.EventType.ASSIGNED_ROLE_ADMIN
        if role == models.Role.ADMIN
        else events_models.EventType.ASSIGNED_ROLE_USER
    )
    events_crud.create_role_change_event(
        db, user, event_type, executor, reason
    )

    return updated_user


router.include_router(session_routes.users_router, tags=["Users - Sessions"])
router.include_router(
    workspaces_routes.router,
    prefix="/{user_id}/workspaces",
    tags=["Users - Workspaces"],
)
router.include_router(
    tokens_routes.user_token_router,
    prefix="/current/tokens",
    tags=["Users - Token"],
)
router.include_router(
    permissions_routes.users_router,
    prefix="/{user_id}/permissions",
    tags=["Users - Permissions"],
)
