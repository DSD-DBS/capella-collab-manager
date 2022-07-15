# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import sqlalchemy.orm.session
from fastapi import Depends, HTTPException

from t4cclient.core.authentication.helper import get_username
from t4cclient.core.authentication.jwt_bearer import JWTBearer
from t4cclient.core.database import get_db, repository_users
from t4cclient.core.database.users import get_user
from t4cclient.schemas.repositories import RepositoryUserPermission, RepositoryUserRole
from t4cclient.schemas.repositories.users import Role


def verify_admin(token=Depends(JWTBearer()), db=Depends(get_db)):
    if not is_admin(token, db):
        raise HTTPException(
            status_code=403,
            detail="The role administrator is required for this transaction.",
        )


def is_admin(token=Depends(JWTBearer()), db=Depends(get_db)) -> bool:
    return get_user(db=db, username=get_username(token)).role == Role.ADMIN


def verify_repository_role(
    repository: str,
    token: JWTBearer,
    db: sqlalchemy.orm.session.Session,
    allowed_roles=["user", "manager", "administrator"],
):
    if not check_repository_role(
        repository=repository, allowed_roles=allowed_roles, token=token, db=db
    ):
        raise HTTPException(
            status_code=403,
            detail=f"One of the roles '{allowed_roles}' in the repository '{repository}' is required.",
        )


def check_repository_role(
    repository: str,
    token: JWTBearer,
    db: sqlalchemy.orm.session.Session,
    allowed_roles=["user", "manager", "administrator"],
) -> bool:

    user = get_user(db=db, username=get_username(token))
    return any(
        (
            "user" in allowed_roles
            and any(repo.repository_name == repository for repo in user.repositories),
            "manager" in allowed_roles
            and any(
                r.repository_name == repository and r.role == RepositoryUserRole.MANAGER
                for r in user.repositories
            ),
            "administrator" in allowed_roles and user.role == Role.ADMIN,
        )
    )


def check_username_not_admin(username: str, db):
    if get_user(db=db, username=username).role == Role.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to edit this user.",
        )


def verify_write_permission(
    repository: str,
    token: JWTBearer,
    db: sqlalchemy.orm.session.Session,
):
    if not check_write_permission(repository, token, db):
        raise HTTPException(
            status_code=403,
            detail=f"You need to have 'Write'-Access in the repository!",
        )


def check_write_permission(
    repository: str,
    token: JWTBearer,
    db: sqlalchemy.orm.session.Session,
) -> bool:

    user = repository_users.get_user_of_repository(db, repository, get_username(token))
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
            detail="The user already exists for this repository.",
        )
