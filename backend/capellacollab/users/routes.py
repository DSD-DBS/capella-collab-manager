# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import typing as t

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import capellacollab.projects.users.crud as project_users
import capellacollab.users.crud as users
from capellacollab.core.authentication.database import is_admin, verify_admin
from capellacollab.core.authentication.helper import get_username
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.authentication.responses import (
    AUTHENTICATION_RESPONSES,
)
from capellacollab.core.database import get_db
from capellacollab.sessions.routes import inject_attrs_in_sessions
from capellacollab.sessions.schema import AdvancedSessionResponse
from capellacollab.users.models import PatchUserRoleRequest, Role, User

router = APIRouter()


@router.get(
    "/",
    response_model=t.List[User],
    responses=AUTHENTICATION_RESPONSES,
)
def get_users(token=Depends(JWTBearer()), db: Session = Depends(get_db)):
    verify_admin(token, db)
    return users.get_all_users(db)


@router.post("/", response_model=User, responses=AUTHENTICATION_RESPONSES)
def create_user(token=Depends(JWTBearer()), db: Session = Depends(get_db)):
    return users.create_user(db, get_username(token))


@router.get(
    "/{username}",
    response_model=User,
    responses=AUTHENTICATION_RESPONSES,
)
def get_user(
    username: str, db: Session = Depends(get_db), token=Depends(JWTBearer())
):
    if username != get_username(token) and not is_admin(token, db):
        raise HTTPException(
            status_code=403,
            detail={
                "reason": "The username does not match with your username. You have to be administrator to see other users."
            },
        )
    return users.get_user(db=db, username=username)


@router.delete(
    "/{username}", status_code=204, responses=AUTHENTICATION_RESPONSES
)
def delete_user(
    username: str, db: Session = Depends(get_db), token=Depends(JWTBearer())
):
    verify_admin(token, db)
    project_users.delete_all_projects_for_user(db, username)
    users.delete_user(db=db, username=username)
    return None


@router.patch("/{username}/roles", responses=AUTHENTICATION_RESPONSES)
def update_role_of_user(
    username: str,
    body: PatchUserRoleRequest,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    verify_admin(token, db)
    users.find_or_create_user(db, username)
    if body.role == Role.ADMIN:
        project_users.delete_all_projects_for_user(db, username)
    return users.update_role_of_user(db, username, body.role)


# TODO: This is actually a sessions route (sessions/{username}?)
@router.get(
    "/{username}/sessions", response_model=t.List[AdvancedSessionResponse]
)
def get_sessions_for_user(
    username: str, db: Session = Depends(get_db), token=Depends(JWTBearer())
):
    if username != get_username(token) and not is_admin(token, db):
        raise HTTPException(
            status_code=403,
            detail={
                "reason": "You can only see your own sessions.",
                "technical": "If you are a project lead or administrator, please use the /sessions endpoint",
            },
        )

    user = users.get_user(db, username)
    return inject_attrs_in_sessions(user.sessions)
