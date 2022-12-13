# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import capellacollab.projects.users.crud as project_crud
import capellacollab.users.events.crud as event_crud
from capellacollab.core.authentication.database import RoleVerification
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.database import get_db
from capellacollab.sessions.routes import inject_attrs_in_sessions
from capellacollab.sessions.schema import OwnSessionResponse
from capellacollab.users.events.models import EventType
from capellacollab.users.events.routes import router as router_events

from . import crud
from .injectables import get_existing_user, get_own_user
from .models import DatabaseUser, PatchUserRoleRequest, PostUser, Role, User

router = APIRouter(
    dependencies=[Depends(RoleVerification(required_role=Role.USER))]
)


@router.get("/current", response_model=User)
def get_current_user(
    user: DatabaseUser = Depends(get_own_user),
) -> DatabaseUser:
    return user


@router.get(
    "/{user_id}",
    response_model=User,
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
)
def get_user(user: DatabaseUser = Depends(get_existing_user)) -> DatabaseUser:
    return user


@router.get(
    "/",
    response_model=list[User],
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
)
def get_users(db: Session = Depends(get_db)) -> list[DatabaseUser]:
    return crud.get_users(db)


@router.post(
    "/",
    response_model=User,
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
)
def create_user(
    post_user: PostUser,
    own_user: DatabaseUser = Depends(get_own_user),
    db: Session = Depends(get_db),
):
    created_user = crud.create_user(db, post_user.name)
    event_crud.create_user_creation_event(
        db=db, user=created_user, executor=own_user, reason=post_user.reason
    )
    return created_user


@router.patch(
    "/{user_id}/roles",
    response_model=User,
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
)
def update_role_of_user(
    patch_user: PatchUserRoleRequest,
    user: DatabaseUser = Depends(get_existing_user),
    own_user: DatabaseUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DatabaseUser:
    if (role := patch_user.role) == Role.ADMIN:
        project_crud.delete_all_projects_for_user(db, user.id)

    updated_user = crud.update_role_of_user(db, user, role)

    event_type = (
        EventType.ASSIGNED_ROLE_ADMIN
        if role == Role.ADMIN
        else EventType.ASSIGNED_ROLE_USER
    )
    event_crud.create_role_change_event(
        db, user, event_type, own_user, patch_user.reason
    )

    return updated_user


@router.delete(
    "/{user_id}",
    status_code=204,
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
)
def delete_user(
    user: DatabaseUser = Depends(get_existing_user),
    db: Session = Depends(get_db),
):
    project_crud.delete_all_projects_for_user(db, user)
    crud.delete_user(db, user)


# TODO: This is actually a sessions route (sessions/{username}?)
@router.get("/{user_id}/sessions", response_model=list[OwnSessionResponse])
def get_sessions_for_user(
    user: DatabaseUser = Depends(get_existing_user),
    current_user: DatabaseUser = Depends(get_own_user),
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    if user != current_user and not RoleVerification(
        required_role=Role.ADMIN, verify=False
    )(token, db):
        raise HTTPException(
            status_code=403,
            detail={
                "reason": "You can only see your own sessions.",
                "technical": "If you are a project lead or administrator, please use the /sessions endpoint",
            },
        )

    return inject_attrs_in_sessions(user.sessions)


router.include_router(router_events, tags=["Users - History"])
