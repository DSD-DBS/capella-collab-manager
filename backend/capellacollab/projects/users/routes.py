# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing as t

from fastapi import APIRouter, Depends, HTTPException
from requests import HTTPError
from sqlalchemy.orm import Session

import capellacollab.users.crud as users
from capellacollab.core.authentication.database import (
    ProjectRoleVerification,
    RoleVerification,
)
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.database import get_db
from capellacollab.projects.capellamodels.injectables import (
    get_existing_project,
)
from capellacollab.projects.models import DatabaseProject
from capellacollab.projects.users.models import (
    PatchProjectUser,
    PostProjectUser,
    ProjectUser,
    ProjectUserAssociation,
    ProjectUserPermission,
    ProjectUserRole,
)
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
    db: Session = Depends(get_db),
) -> ProjectUserAssociation:
    user = users.find_or_create_user(db, post_project_user.username)

    check_user_not_admin(user)
    check_user_not_in_project(project, user)

    if post_project_user.role == ProjectUserRole.MANAGER:
        post_project_user.permission = ProjectUserPermission.WRITE

    return crud.add_user_to_project(
        db, project, user, post_project_user.role, post_project_user.permission
    )


@router.patch(
    "/{user_id}",
    status_code=204,
    dependencies=[
        Depends(ProjectRoleVerification(required_role=ProjectUserRole.MANAGER))
    ],
)
def patch_project_user(
    patch_project_user: PatchProjectUser,
    user: DatabaseUser = Depends(get_existing_user),
    project: DatabaseProject = Depends(get_existing_project),
    db: Session = Depends(get_db),
):
    check_user_not_admin(user)
    if patch_project_user.role:
        crud.change_role_of_user_in_project(
            db, project, user, patch_project_user.role
        )

    if patch_project_user.permission:
        repo_user = crud.get_user_of_project(
            db,
            project,
            user,
        )

        if repo_user.role == ProjectUserRole.MANAGER:
            raise HTTPException(
                status_code=403,
                detail={
                    "reason": "You are not allowed to set the permission of project leads!"
                },
            )
        crud.change_permission_of_user_in_project(
            db, project, user, patch_project_user.permission
        )


@router.delete(
    "/{user_id}",
    status_code=204,
    dependencies=[
        Depends(ProjectRoleVerification(required_role=ProjectUserRole.MANAGER))
    ],
)
def remove_user_from_project(
    project: DatabaseProject = Depends(get_existing_project),
    user: DatabaseUser = Depends(get_existing_user),
    db: Session = Depends(get_db),
):
    check_user_not_admin(user)
    crud.delete_user_from_project(db, project, user)
    return None
