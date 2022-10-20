# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing as t

from fastapi import APIRouter, Depends, HTTPException
from requests import HTTPError
from sqlalchemy.orm import Session

import capellacollab.projects.users.crud as project_users
import capellacollab.projects.users.models as schema_projects
import capellacollab.users.crud as users
from capellacollab.core.authentication.database import verify_project_role
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.database import get_db
from capellacollab.users.models import Role, User

from . import crud

router = APIRouter()


def check_user_id_not_admin(user_id: int, db):
    """
    Administrators have access to all projects.
    We have to prevent that they get roles in projects.
    """
    if users.get_user_by_id(db, user_id).role == Role.ADMIN:
        raise HTTPException(
            status_code=403,
            detail={"reason": "You are not allowed to edit this user."},
        )


def check_username_not_in_project(
    project: str,
    user: User,
    db: Session,
):
    if project_users.get_user_of_project(
        db=db, project_name=project, user_id=user.id
    ):
        raise HTTPException(
            status_code=409,
            detail={
                "reason": "The user already exists in this project.",
            },
        )


@router.get(
    "/",
    response_model=t.List[schema_projects.ProjectUser],
)
def get_users_for_project(
    project: str,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    verify_project_role(
        project, allowed_roles=["manager", "administrator"], token=token, db=db
    )
    return crud.get_users_of_project(db, project)


@router.post(
    "/",
    response_model=schema_projects.ProjectUser,
)
def add_user_to_project(
    project: str,
    body: schema_projects.PostProjectUser,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    verify_project_role(
        project, allowed_roles=["manager", "administrator"], token=token, db=db
    )
    user = users.find_or_create_user(db, body.username)
    check_username_not_in_project(project, user, db=db)

    check_user_id_not_admin(user.id, db)
    if body.role == schema_projects.ProjectUserRole.MANAGER:
        body.permission = schema_projects.ProjectUserPermission.WRITE
    return crud.add_user_to_project(
        db, project, body.role, user.id, body.permission
    )


@router.patch(
    "/{user_id}",
    status_code=204,
)
def patch_project_user(
    project: str,
    user_id: int,
    body: schema_projects.PatchProjectUser,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    verify_project_role(
        project,
        allowed_roles=["user", "manager", "administrator"],
        token=token,
        db=db,
    )

    if body.role:
        verify_project_role(
            project,
            allowed_roles=["manager", "administrator"],
            token=token,
            db=db,
        )
        check_user_id_not_admin(user_id, db)
        crud.change_role_of_user_in_project(db, project, body.role, user_id)

    if body.permission:
        verify_project_role(
            project,
            allowed_roles=["manager", "administrator"],
            token=token,
            db=db,
        )
        check_user_id_not_admin(user_id, db)
        repo_user = crud.get_user_of_project(
            db,
            project,
            user_id,
        )

        if repo_user.role == schema_projects.ProjectUserRole.MANAGER:
            raise HTTPException(
                status_code=403,
                detail={
                    "reason": "You are not allowed to set the permission of project leads!"
                },
            )
        crud.change_permission_of_user_in_project(
            db, project, body.permission, user_id
        )
    return None


@router.delete(
    "/{user_id}",
    status_code=204,
)
def remove_user_from_project(
    project: str,
    user_id: int,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    verify_project_role(
        project, allowed_roles=["manager", "administrator"], token=token, db=db
    )
    check_user_id_not_admin(user_id, db)
    crud.delete_user_from_project(db, project, user_id)
    return None
