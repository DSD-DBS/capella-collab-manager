# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import typing as t

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import capellacollab.projects.users.crud as project_users
from capellacollab.core.authentication.database import (
    RoleVerification,
    is_admin,
)
from capellacollab.core.authentication.helper import get_username
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.authentication.responses import (
    AUTHENTICATION_RESPONSES,
)
from capellacollab.core.database import get_db
from capellacollab.sessions.routes import inject_attrs_in_sessions
from capellacollab.sessions.schema import AdvancedSessionResponse
from capellacollab.users.models import (
    BaseUser,
    PatchUserRoleRequest,
    Role,
    User,
)

from . import crud, injectables

router = APIRouter()


@router.get(
    "/",
    response_model=t.List[User],
    responses=AUTHENTICATION_RESPONSES,
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
)
def get_users(
    db: Session = Depends(get_db),
):
    return crud.get_all_users(db)


@router.post(
    "/",
    response_model=User,
    responses=AUTHENTICATION_RESPONSES,
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
)
def create_user(body: BaseUser, db: Session = Depends(get_db)):
    return crud.create_user(db, body.name)


@router.get(
    "/current",
    response_model=User,
    responses=AUTHENTICATION_RESPONSES,
    dependencies=[Depends(RoleVerification(required_role=Role.USER))],
)
def get_current_user(
    db: Session = Depends(get_db), token=Depends(JWTBearer())
):
    return crud.get_user_by_name(db=db, username=get_username(token))


@router.get(
    "/{user_id}",
    response_model=User,
    responses=AUTHENTICATION_RESPONSES,
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return crud.get_user_by_id(db=db, user_id=user_id)


@router.delete(
    "/{user_id}",
    status_code=204,
    responses=AUTHENTICATION_RESPONSES,
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
)
def delete_user(user_id: str, db: Session = Depends(get_db)):
    project_users.delete_all_projects_for_user(db, user_id)
    crud.delete_user(db=db, user_id=user_id)
    return None


@router.patch(
    "/{user_id}/roles",
    responses=AUTHENTICATION_RESPONSES,
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
)
def update_role_of_user(
    user_id: str,
    body: PatchUserRoleRequest,
    db: Session = Depends(get_db),
):
    if body.role == Role.ADMIN:
        project_users.delete_all_projects_for_user(db, user_id)
    return crud.update_role_of_user(db, user_id, body.role)


# TODO: This is actually a sessions route (sessions/{username}?)
@router.get(
    "/{user_id}/sessions", response_model=t.List[AdvancedSessionResponse]
)
def get_sessions_for_user(
    user: User = Depends(injectables.get_user),
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    if user.name != get_username(token) and not is_admin(token, db):
        raise HTTPException(
            status_code=403,
            detail={
                "reason": "You can only see your own sessions.",
                "technical": "If you are a project lead or administrator, please use the /sessions endpoint",
            },
        )

    return inject_attrs_in_sessions(user.sessions)
