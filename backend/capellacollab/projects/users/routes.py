# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing as t

from fastapi import APIRouter, Depends, HTTPException
from requests import HTTPError, Session

import capellacollab.extensions.modelsources.t4c.connection as t4c_manager
import capellacollab.projects.users.models as schema_projects
import capellacollab.users.crud as users
from capellacollab.core.authentication.database import (
    check_username_not_admin,
    check_username_not_in_project,
    is_admin,
    verify_project_role,
    verify_write_permission,
)
from capellacollab.core.authentication.helper import get_username
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.authentication.responses import (
    AUTHENTICATION_RESPONSES,
)
from capellacollab.core.database import get_db

from . import crud

router = APIRouter()


@router.get(
    "/",
    response_model=t.List[schema_projects.ProjectUser],
    responses=AUTHENTICATION_RESPONSES,
)
def get_users_for_project(
    project: str,
    username: t.Union[str, None] = None,
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
    responses=AUTHENTICATION_RESPONSES,
)
def add_user_to_project(
    project: str,
    body: schema_projects.ProjectUser,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    verify_project_role(
        project, allowed_roles=["manager", "administrator"], token=token, db=db
    )

    check_username_not_in_project(project, body.username, db=db)

    users.find_or_create_user(db, body.username)
    check_username_not_admin(body.username, db)
    if body.role == schema_projects.ProjectUserRole.MANAGER:
        body.permission = schema_projects.ProjectUserPermission.WRITE
    if body.permission == schema_projects.ProjectUserPermission.WRITE:
        t4c_manager.add_user_to_repository(
            project, body.username, is_admin=False
        )
    return crud.add_user_to_project(
        db, project, body.role, body.username, body.permission
    )


@router.patch(
    "/{username}",
    status_code=204,
    responses=AUTHENTICATION_RESPONSES,
)
def patch_project_user(
    project: str,
    username: str,
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
        check_username_not_admin(username, db)
        crud.change_role_of_user_in_project(db, project, body.role, username)
    if body.password:
        verify_project_role(
            project,
            token=token,
            db=db,
        )
        verify_write_permission(project, token, db)

        admin = is_admin(token, db)
        if not admin and get_username(token) != username:
            raise HTTPException(
                status_code=403,
                detail={
                    "reason": "The username does not match with your user. You have to be administrator to edit other users."
                },
            )

        try:
            t4c_manager.update_password_of_user(
                project, username, body.password
            )
        except HTTPError as err:
            if err.response.status_code == 404:
                t4c_manager.add_user_to_repository(
                    project, username, body.password, is_admin=admin
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail={"reason": "Invalid response from T4C server."},
                ) from err

    if body.permission:
        verify_project_role(
            project,
            allowed_roles=["manager", "administrator"],
            token=token,
            db=db,
        )
        check_username_not_admin(username, db)
        repo_user = crud.get_user_of_project(
            db,
            project,
            username,
        )

        if repo_user.role == schema_projects.ProjectUserRole.MANAGER:
            raise HTTPException(
                status_code=403,
                detail={
                    "reason": "You are not allowed to set the permission of project leads!"
                },
            )
        crud.change_permission_of_user_in_project(
            db, project, body.permission, username
        )
    return None


@router.delete(
    "/{username}",
    status_code=204,
    responses=AUTHENTICATION_RESPONSES,
)
def remove_user_from_project(
    project: str,
    username: str,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    verify_project_role(
        project, allowed_roles=["manager", "administrator"], token=token, db=db
    )
    check_username_not_admin(username, db)
    t4c_manager.remove_user_from_repository(project, username)
    crud.delete_user_from_project(db, project, username)
    return None
