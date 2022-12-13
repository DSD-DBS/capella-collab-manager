# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing as t

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

import capellacollab.users.crud as users
import capellacollab.users.events.crud as event_crud
from capellacollab.core.authentication.database import (
    ProjectRoleVerification,
    RoleVerification,
)
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.database import get_db
from capellacollab.projects.models import DatabaseProject
from capellacollab.projects.toolmodels.injectables import get_existing_project
from capellacollab.projects.users.core import (
    create_add_user_to_project_events,
    get_project_permission_event_type,
    get_project_role_event_type,
)
from capellacollab.projects.users.models import (
    PatchProjectUser,
    PostProjectUser,
    ProjectUser,
    ProjectUserAssociation,
    ProjectUserPermission,
    ProjectUserRole,
)
from capellacollab.users.events.models import EventType
from capellacollab.users.injectables import get_own_user
from capellacollab.users.models import DatabaseUser, Role, User

from . import crud
from .injectables import get_existing_user

router = APIRouter()


def check_user_not_admin(user: DatabaseUser) -> bool:
    """
    Administrators have access to all projects.
    We have to prevent that they get roles in projects.
    """
    if user.role == Role.ADMIN:
        raise HTTPException(
            status_code=403,
            detail={"reason": "You are not allowed to edit this user."},
        )
    return True


def check_user_not_in_project(project: DatabaseProject, user: DatabaseUser):
    if user in project.users:
        raise HTTPException(
            status_code=409,
            detail={
                "reason": "The user already exists in this project.",
            },
        )


@router.get("/current", response_model=ProjectUser)
def get_current_user(
    user: DatabaseUser = Depends(get_own_user),
    project: DatabaseProject = Depends(get_existing_project),
    db: Session = Depends(get_db),
    token: JWTBearer = Depends(JWTBearer()),
) -> ProjectUserAssociation | ProjectUser:
    if RoleVerification(required_role=Role.ADMIN, verify=False)(token, db):
        return ProjectUser(
            role=ProjectUserRole.ADMIN,
            permission=ProjectUserPermission.WRITE,
            user=user,
        )
    return crud.get_user_of_project(db, project, user)


@router.get(
    "/",
    response_model=t.List[ProjectUser],
    dependencies=[
        Depends(ProjectRoleVerification(required_role=ProjectUserRole.MANAGER))
    ],
)
def get_users_for_project(
    project: DatabaseProject = Depends(get_existing_project),
) -> User:
    return project.users


@router.post(
    "/",
    response_model=ProjectUser,
    dependencies=[
        Depends(ProjectRoleVerification(required_role=ProjectUserRole.MANAGER))
    ],
)
def add_user_to_project(
    post_project_user: PostProjectUser,
    project: DatabaseProject = Depends(get_existing_project),
    own_user: DatabaseUser = Depends(get_own_user),
    db: Session = Depends(get_db),
) -> ProjectUserAssociation:
    if not (user := users.get_user_by_name(db, post_project_user.username)):
        raise HTTPException(
            404,
            {
                "reason": f"The user with username “{post_project_user.username}” does not exist"
            },
        )
    check_user_not_admin(user)
    check_user_not_in_project(project, user)

    if post_project_user.role == ProjectUserRole.MANAGER:
        post_project_user.permission = ProjectUserPermission.WRITE

    association = crud.add_user_to_project(
        db, project, user, post_project_user.role, post_project_user.permission
    )
    create_add_user_to_project_events(
        post_project_user, user, project, own_user, db
    )

    return association


@router.patch(
    "/{user_id}",
    status_code=204,
    dependencies=[
        Depends(ProjectRoleVerification(required_role=ProjectUserRole.MANAGER))
    ],
)
def update_project_user(
    patch_project_user: PatchProjectUser,
    user: DatabaseUser = Depends(get_existing_user),
    project: DatabaseProject = Depends(get_existing_project),
    own_user: DatabaseUser = Depends(get_own_user),
    db: Session = Depends(get_db),
):
    check_user_not_admin(user)
    if role := patch_project_user.role:
        crud.change_role_of_user_in_project(db, project, user, role)

        event_crud.create_project_change_event(
            db=db,
            user=user,
            event_type=get_project_role_event_type(role),
            executor=own_user,
            project=project,
            reason=patch_project_user.reason,
        )

    if permission := patch_project_user.permission:
        project_user = crud.get_user_of_project(db, project, user)

        if project_user.role == ProjectUserRole.MANAGER:
            raise HTTPException(
                status_code=403,
                detail={
                    "reason": "You are not allowed to set the permission of project leads!"
                },
            )
        crud.change_permission_of_user_in_project(
            db, project, user, permission
        )

        event_crud.create_project_change_event(
            db=db,
            user=user,
            event_type=get_project_permission_event_type(permission),
            executor=own_user,
            project=project,
            reason=patch_project_user.reason,
        )


@router.delete(
    "/{user_id}",
    status_code=204,
    dependencies=[
        Depends(ProjectRoleVerification(required_role=ProjectUserRole.MANAGER))
    ],
)
def remove_user_from_project(
    reason: str = Body(),
    project: DatabaseProject = Depends(get_existing_project),
    user: DatabaseUser = Depends(get_existing_user),
    own_user: DatabaseUser = Depends(get_own_user),
    db: Session = Depends(get_db),
):
    check_user_not_admin(user)

    crud.delete_user_from_project(db, project, user)
    event_crud.create_project_change_event(
        db, user, EventType.REMOVED_FROM_PROJECT, own_user, project, reason
    )
