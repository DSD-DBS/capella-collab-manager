# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from collections import abc

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.projects.users import crud as projects_users_crud
from capellacollab.sessions import routes as session_routes
from capellacollab.users.events import crud as events_crud
from capellacollab.users.events import models as events_models
from capellacollab.users.events import routes as events_routes
from capellacollab.users.tokens import routes as tokens_routes

from . import crud, injectables, models

router = fastapi.APIRouter(
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(required_role=models.Role.USER)
        )
    ]
)


@router.get("/current", response_model=models.User)
def get_current_user(
    user: models.DatabaseUser = fastapi.Depends(injectables.get_own_user),
) -> models.DatabaseUser:
    return user


@router.get(
    "/{user_id}",
    response_model=models.User,
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(required_role=models.Role.ADMIN)
        )
    ],
)
def get_user(
    user: models.DatabaseUser = fastapi.Depends(injectables.get_existing_user),
) -> models.DatabaseUser:
    return user


@router.get(
    "",
    response_model=list[models.User],
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(required_role=models.Role.ADMIN)
        )
    ],
)
def get_users(
    db: orm.Session = fastapi.Depends(database.get_db),
) -> abc.Sequence[models.DatabaseUser]:
    return crud.get_users(db)


@router.post(
    "",
    response_model=models.User,
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(required_role=models.Role.ADMIN)
        )
    ],
)
def create_user(
    post_user: models.PostUser,
    own_user: models.DatabaseUser = fastapi.Depends(injectables.get_own_user),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    created_user = crud.create_user(db, post_user.name)
    events_crud.create_user_creation_event(
        db=db, user=created_user, executor=own_user, reason=post_user.reason
    )
    return created_user


@router.patch(
    "/{user_id}/roles",
    response_model=models.User,
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(required_role=models.Role.ADMIN)
        )
    ],
)
def update_role_of_user(
    patch_user: models.PatchUserRoleRequest,
    user: models.DatabaseUser = fastapi.Depends(injectables.get_existing_user),
    own_user: models.DatabaseUser = fastapi.Depends(get_current_user),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.DatabaseUser:
    if (role := patch_user.role) == models.Role.ADMIN:
        projects_users_crud.delete_projects_for_user(db, user.id)

    updated_user = crud.update_role_of_user(db, user, role)

    event_type = (
        events_models.EventType.ASSIGNED_ROLE_ADMIN
        if role == models.Role.ADMIN
        else events_models.EventType.ASSIGNED_ROLE_USER
    )
    events_crud.create_role_change_event(
        db, user, event_type, own_user, patch_user.reason
    )

    return updated_user


@router.delete(
    "/{user_id}",
    status_code=204,
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(required_role=models.Role.ADMIN)
        )
    ],
)
def delete_user(
    user: models.DatabaseUser = fastapi.Depends(injectables.get_existing_user),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    projects_users_crud.delete_projects_for_user(db, user.id)
    events_crud.delete_all_events_user_involved_in(db, user.id)
    crud.delete_user(db, user)


router.include_router(session_routes.users_router, tags=["Users - Sessions"])
router.include_router(events_routes.router, tags=["Users - History"])
router.include_router(
    tokens_routes.router, prefix="/current/tokens", tags=["Users - Token"]
)
