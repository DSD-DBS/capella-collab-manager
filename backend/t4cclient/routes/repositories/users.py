import typing as t

import t4cclient.extensions.modelsources.t4c.connection as t4c_manager
import t4cclient.schemas.repositories as schema_repositories
from fastapi import APIRouter, Depends, HTTPException
from requests import HTTPError, Session
from t4cclient.config import USERNAME_CLAIM
from t4cclient.core.authentication.database import (check_username_not_admin,
                                                    is_admin,
                                                    verify_repository_role,
                                                    verify_write_permission)
from t4cclient.core.authentication.helper import get_username
from t4cclient.core.authentication.jwt_bearer import JWTBearer
from t4cclient.core.database import get_db, repository_users, users
from t4cclient.routes.open_api_configuration import AUTHENTICATION_RESPONSES

router = APIRouter()


@router.get(
    "/",
    response_model=t.List[schema_repositories.RepositoryUser],
    responses=AUTHENTICATION_RESPONSES,
)
def get_users_for_repository(
    project: str, db: Session = Depends(get_db), token=Depends(JWTBearer())
):
    verify_repository_role(
        project, allowed_roles=["manager", "administrator"], token=token, db=db
    )
    return repository_users.get_users_of_repository(db, project)


@router.post(
    "/",
    response_model=schema_repositories.RepositoryUser,
    responses=AUTHENTICATION_RESPONSES,
)
def add_user_to_repository(
    project: str,
    body: schema_repositories.PostRepositoryUser,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    verify_repository_role(
        project, allowed_roles=["manager", "administrator"], token=token, db=db
    )
    users.find_or_create_user(db, body.username)
    check_username_not_admin(body.username, db)
    if body.role == schema_repositories.RepositoryUserRole.MANAGER:
        body.permission == schema_repositories.RepositoryUserPermission.WRITE
    if body.permission == schema_repositories.RepositoryUserPermission.WRITE:
        t4c_manager.add_user_to_repository(project, body.username)
    return repository_users.add_user_to_repository(
        db, project, body.role, body.username, body.permission
    )


@router.patch(
    "/{username}",
    status_code=204,
    responses=AUTHENTICATION_RESPONSES,
)
def patch_repository_user(
    project: str,
    username: str,
    body: schema_repositories.PatchRepositoryUser,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    verify_repository_role(
        project,
        allowed_roles=["user", "manager", "administrator"],
        token=token,
        db=db,
    )

    if body.role:
        verify_repository_role(
            project,
            allowed_roles=["manager", "administrator"],
            token=token,
            db=db,
        )
        check_username_not_admin(username, db)
        repository_users.change_role_of_user_in_repository(
            db, project, body.role, username
        )
    if body.password:
        verify_repository_role(
            project,
            token=token,
            db=db,
        )
        verify_write_permission(project, token, db)
        if not is_admin(token, db) and get_username(token) != username:
            raise HTTPException(
                status_code=403,
                detail="The username does not match with your user. You have to be administrator to edit other users.",
            )

        try:
            t4c_manager.update_password_of_user(project, username, body.password)
        except HTTPError as err:
            if err.response.status_code == 404:
                t4c_manager.add_user_to_repository(project, username, body.password)
            else:
                raise HTTPException(
                    status_code=500,
                    detail="Invalid response from T4C Server",
                )

    if body.permission:
        verify_repository_role(
            project,
            allowed_roles=["manager", "administrator"],
            token=token,
            db=db,
        )
        check_username_not_admin(username, db)
        repo_user = repository_users.get_user_of_repository(
            db,
            project,
            username,
        )

        if repo_user.role == schema_repositories.RepositoryUserRole.MANAGER:
            raise HTTPException(
                status_code=403,
                detail="You are not allowed to set the permission of managers!",
            )
        repository_users.change_permission_of_user_in_repository(
            db, project, body.permission, username
        )


@router.delete(
    "/{username}",
    status_code=204,
    responses=AUTHENTICATION_RESPONSES,
)
def remove_user_from_repository(
    project: str,
    username: str,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    verify_repository_role(
        project, allowed_roles=["manager", "administrator"], token=token, db=db
    )
    check_username_not_admin(username, db)
    t4c_manager.remove_user_from_repository(project, username)
    repository_users.delete_user_from_repository(db, project, username)
