# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from collections import abc

import fastapi
from fastapi import status
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.events import crud as events_crud
from capellacollab.events import models as events_models
from capellacollab.projects import crud as projects_crud
from capellacollab.projects import models as projects_models
from capellacollab.projects.users import crud as projects_users_crud
from capellacollab.sessions import routes as session_routes
from capellacollab.users import injectables as users_injectables
from capellacollab.users import models as users_models
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
)
def get_user(
    own_user: models.DatabaseUser = fastapi.Depends(injectables.get_own_user),
    user: models.DatabaseUser = fastapi.Depends(injectables.get_existing_user),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.DatabaseUser:
    if (
        user.id == own_user.id
        or len(projects_crud.get_common_projects_for_users(db, own_user, user))
        > 0
        or auth_injectables.RoleVerification(
            required_role=models.Role.ADMIN, verify=False
        )(own_user.name, db)
    ):
        return user
    else:
        raise fastapi.HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "err_code": "NO_PROJECTS_IN_COMMON",
                "reason": "You need at least one project in common to access the user profile of another user.",
            },
        )


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


@router.get(
    "/{user_id}/common-projects",
    response_model=list[projects_models.Project],
    tags=["Projects"],
)
def get_common_projects(
    user_for_common_projects: models.DatabaseUser = fastapi.Depends(
        injectables.get_existing_user
    ),
    user: models.DatabaseUser = fastapi.Depends(injectables.get_own_user),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> list[projects_models.DatabaseProject]:
    if user.role == models.Role.ADMIN:
        return [
            association.project
            for association in user_for_common_projects.projects
        ]
    projects = projects_crud.get_common_projects_for_users(
        db, user, user_for_common_projects
    )
    return list(projects)


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


@router.get(
    "/{user_id}/events",
    response_model=list[events_models.HistoryEvent],
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.ADMIN
            )
        )
    ],
)
def get_user_events(
    user: users_models.DatabaseUser = fastapi.Depends(
        users_injectables.get_existing_user
    ),
) -> list[events_models.DatabaseUserHistoryEvent]:
    return user.events


def get_projects_for_user(
    user: models.DatabaseUser, db: orm.Session
) -> list[projects_models.DatabaseProject]:
    if user.role != models.Role.ADMIN:
        return [association.project for association in user.projects]
    else:
        return list(projects_crud.get_projects(db))


router.include_router(session_routes.users_router, tags=["Users - Sessions"])
router.include_router(
    tokens_routes.router, prefix="/current/tokens", tags=["Users - Token"]
)
