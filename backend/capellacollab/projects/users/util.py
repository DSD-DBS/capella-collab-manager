# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from sqlalchemy.orm import Session

import capellacollab.users.events.crud as event_crud
from capellacollab.projects.models import DatabaseProject
from capellacollab.projects.users.models import (
    PostProjectUser,
    ProjectUserPermission,
    ProjectUserRole,
)
from capellacollab.users.events.models import EventType
from capellacollab.users.models import DatabaseUser


def create_add_user_to_project_events(
    post_project_user: PostProjectUser,
    user: DatabaseUser,
    project: DatabaseProject,
    executor: DatabaseUser,
    db: Session,
):
    reason: str = post_project_user.reason
    project_role: ProjectUserRole = post_project_user.role

    event_crud.create_project_change_event(
        db, user, EventType.ADDED_TO_PROJECT, executor, project, reason
    )

    event_crud.create_project_change_event(
        db=db,
        user=user,
        event_type=get_project_role_event_type(post_project_user.role),
        executor=executor,
        project=project,
        reason=reason,
    )

    if not project_role == ProjectUserRole.MANAGER:
        event_crud.create_project_change_event(
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
    permission: ProjectUserPermission,
) -> EventType:
    return (
        EventType.ASSIGNED_PROJECT_PERMISSION_READ_ONLY
        if permission == ProjectUserPermission.READ
        else EventType.ASSIGNED_PROJECT_PERMISSION_READ_WRITE
    )


def get_project_role_event_type(role: ProjectUserRole) -> EventType:
    return (
        EventType.ASSIGNED_PROJECT_ROLE_USER
        if role == ProjectUserRole.USER
        else EventType.ASSIGNED_PROJECT_ROLE_MANAGER
    )
