import typing as t

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from t4cclient.config import USERNAME_CLAIM
from t4cclient.core.database import get_db, repository_users, users
from t4cclient.core.oauth.database import is_admin, verify_admin
from t4cclient.core.oauth.jwt_bearer import JWTBearer
from t4cclient.routes.open_api_configuration import AUTHENTICATION_RESPONSES
from t4cclient.routes.sessions import inject_attrs_in_sessions
from t4cclient.schemas.repositories.users import (
    GetUserResponse,
    PatchUserRoleRequest,
    Role,
)
from t4cclient.schemas.sessions import AdvancedSessionResponse

router = APIRouter()


@router.get(
    "/", response_model=t.List[GetUserResponse], responses=AUTHENTICATION_RESPONSES
)
def get_users(token=Depends(JWTBearer()), db: Session = Depends(get_db)):
    verify_admin(token, db)
    return users.get_all_users(db)


@router.post("/", response_model=GetUserResponse, responses=AUTHENTICATION_RESPONSES)
def create_user(token=Depends(JWTBearer()), db: Session = Depends(get_db)):
    return users.create_user(db, token[USERNAME_CLAIM])


@router.get(
    "/{username}", response_model=GetUserResponse, responses=AUTHENTICATION_RESPONSES
)
def get_user(username: str, db: Session = Depends(get_db), token=Depends(JWTBearer())):
    if username != token[USERNAME_CLAIM] and not is_admin(token, db):
        raise HTTPException(
            status_code=403,
            detail="The username does not match with your username. You have to be administrator to see other users.",
        )
    return users.get_user(db=db, username=username)


@router.delete("/{username}", status_code=204, responses=AUTHENTICATION_RESPONSES)
def delete_user(
    username: str, db: Session = Depends(get_db), token=Depends(JWTBearer())
):
    verify_admin(token, db)
    repository_users.delete_all_repositories_for_user(db, username)
    users.delete_user(db=db, username=username)


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
        repository_users.delete_all_repositories_for_user(db, username)
    return users.update_role_of_user(db, username, body.role)


@router.get("/{username}/sessions", response_model=t.List[AdvancedSessionResponse])
def get_sessions_for_user(
    username: str, db: Session = Depends(get_db), token=Depends(JWTBearer())
):
    if username != token[USERNAME_CLAIM] and not is_admin(token, db):
        raise HTTPException(
            status_code=403,
            detail="You can only see your own sessions. If you are a manager, please use the /sessions endpoint.",
        )

    user = users.get_user(db, username)
    return inject_attrs_in_sessions(user.sessions)
