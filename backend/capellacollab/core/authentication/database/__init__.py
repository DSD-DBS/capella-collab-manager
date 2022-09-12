# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import sqlalchemy.orm.session
from fastapi import Depends, HTTPException

import capellacollab.projects.users.crud as repository_users
from capellacollab.core.authentication.helper import get_username
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.database import get_db
from capellacollab.core.database.users import get_user
from capellacollab.projects.users.models import (
    RepositoryUserPermission,
    RepositoryUserRole,
    Role,
)
from capellacollab.sessions.database import get_session_by_id
from capellacollab.settings.modelsources.git import crud


def verify_admin(token=Depends(JWTBearer()), db=Depends(get_db)):
    if not is_admin(token, db):
        raise HTTPException(
            status_code=403,
            detail={
                "reason": "The role administrator is required for this transaction.",
            },
        )


def is_admin(token=Depends(JWTBearer()), db=Depends(get_db)) -> bool:
    return get_user(db=db, username=get_username(token)).role == Role.ADMIN


def verify_project_role(
    repository: str,
    token: JWTBearer,
    db: sqlalchemy.orm.session.Session,
    allowed_roles=["user", "manager", "administrator"],
):
    if not check_project_role(
        repository=repository, allowed_roles=allowed_roles, token=token, db=db
    ):
        raise HTTPException(
            status_code=403,
            detail={
                "reason": f"One of the roles '{allowed_roles}' in the repository '{repository}' is required.",
            },
        )


def check_project_role(
    repository: str,
    token: JWTBearer,
    db: sqlalchemy.orm.session.Session,
    allowed_roles=["user", "manager", "administrator"],
) -> bool:

    user = get_user(db=db, username=get_username(token))
    return any(
        (
            "user" in allowed_roles
            and any(project.name == repository for project in user.projects),
            "manager" in allowed_roles
            and any(
                project.name == repository
                and project.role == RepositoryUserRole.MANAGER
                for project in user.projects
            ),
            "administrator" in allowed_roles and user.role == Role.ADMIN,
        )
    )


def check_username_not_admin(username: str, db):
    if get_user(db=db, username=username).role == Role.ADMIN:
        raise HTTPException(
            status_code=403,
            detail={"reason": "You are not allowed to edit this user."},
        )


def verify_write_permission(
    repository: str,
    token: JWTBearer,
    db: sqlalchemy.orm.session.Session,
):
    if not check_write_permission(repository, token, db):
        raise HTTPException(
            status_code=403,
            detail={
                "reason": "You need to have 'write'-access in the repository!",
            },
        )


def check_write_permission(
    repository: str,
    token: JWTBearer,
    db: sqlalchemy.orm.session.Session,
) -> bool:

    user = repository_users.get_user_of_repository(
        db, repository, get_username(token)
    )
    if not user:
        return get_user(db=db, username=get_username(token)).role == Role.ADMIN
    return RepositoryUserPermission.WRITE == user.permission


def check_username_not_in_repository(
    repository: str,
    username: str,
    db: sqlalchemy.orm.session.Session,
):
    user = repository_users.get_user_of_repository(db, repository, username)
    if user:
        raise HTTPException(
            status_code=409,
            detail={
                "reason": "The user already exists in this repository.",
            },
        )


def check_session_belongs_to_user(
    username: str,
    id: str,
    db: sqlalchemy.orm.session.Session,
):
    session = get_session_by_id(db, id)
    if not session.owner_name == username:
        raise HTTPException(
            status_code=403,
            detail={
                "reason": "You are not allowed to upload or get files in this session."
            },
        )


def check_git_settings_instance_exists(
    db: sqlalchemy.orm.session.Session,
    id: int,
):
    instance = crud.get_git_settings(db, id)
    if not instance:
        raise HTTPException(
            status_code=404,
            detail={
                "reason": f"The git instance with id {id} does not exist."
            },
        )
