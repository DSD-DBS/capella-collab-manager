# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from sqlalchemy import orm

from capellacollab.events import crud as events_crud
from capellacollab.events import models as events_models
from capellacollab.projects import models as projects_models
from capellacollab.users import models as users_models

from . import models


def create_add_user_to_project_events(
    post_project_user: models.PostProjectUser,
    user: users_models.DatabaseUser,
    project: projects_models.DatabaseProject,
    executor: users_models.DatabaseUser,
    db: orm.Session,
):
    reason: str = post_project_user.reason
    project_role: models.ProjectUserRole = post_project_user.role

    events_crud.create_project_change_event(
        db,
        user,
        events_models.EventType.ADDED_TO_PROJECT,
        executor,
        project,
        reason,
    )

    events_crud.create_project_change_event(
        db=db,
        user=user,
        event_type=get_project_role_event_type(post_project_user.role),
        executor=executor,
        project=project,
        reason=reason,
    )

    if not project_role == models.ProjectUserRole.MANAGER:
        events_crud.create_project_change_event(
            db=db,
            user=user,
            event_type=get_project_permission_event_type(
                post_project_user.permission
            ),
            executor=executor,
            project=project,
            reason=reason,
        )


def get_project_permission_event_type(
    permission: models.ProjectUserPermission,
) -> events_models.EventType:
    return (
        events_models.EventType.ASSIGNED_PROJECT_PERMISSION_READ_ONLY
        if permission == models.ProjectUserPermission.READ
        else events_models.EventType.ASSIGNED_PROJECT_PERMISSION_READ_WRITE
    )


def get_project_role_event_type(
    role: models.ProjectUserRole,
) -> events_models.EventType:
    return (
        events_models.EventType.ASSIGNED_PROJECT_ROLE_USER
        if role == models.ProjectUserRole.USER
        else events_models.EventType.ASSIGNED_PROJECT_ROLE_MANAGER
    )
