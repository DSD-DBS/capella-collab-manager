# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

# Standard library:
import itertools
import json
import logging
import typing as t

# 3rd party:
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# 1st party:
import capellacollab.extensions.modelsources.git.crud as git_models_crud
import capellacollab.projects.crud as repositories_crud
import capellacollab.projects.users.models as users_models
from capellacollab.core.authentication.database import is_admin, verify_project_role
from capellacollab.core.authentication.helper import get_username
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.credentials import generate_password
from capellacollab.core.database import get_db, users
from capellacollab.core.operators import OPERATOR
from capellacollab.core.services.sessions import inject_attrs_in_sessions
from capellacollab.projects.users.crud import RepositoryUserRole
from capellacollab.routes.open_api_configuration import AUTHENTICATION_RESPONSES
from capellacollab.schemas.sessions import (
    AdvancedSessionResponse,
    GetSessionsResponse,
    GetSessionUsageResponse,
    GuacamoleAuthentication,
    PostSessionRequest,
    WorkspaceType,
)
from capellacollab.sessions import database, guacamole
from capellacollab.sessions.models import DatabaseSession
from capellacollab.sessions.sessions import get_last_seen, inject_attrs_in_sessions

router = APIRouter()
log = logging.getLogger(__name__)


@router.get("/", response_model=t.List[GetSessionsResponse])
def get_current_sessions(db: Session = Depends(get_db), token=Depends(JWTBearer())):
    if is_admin(token, db):
        return inject_attrs_in_sessions(database.get_all_sessions(db))

    db_user = users.get_user(db=db, username=get_username(token))
    if not any(
        repo_user.role == RepositoryUserRole.MANAGER
        for repo_user in db_user.repositories
    ):
        raise HTTPException(
            status_code=403,
            detail="You have to be project manager for at least one repository.",
        )
    return inject_attrs_in_sessions(
        list(
            itertools.chain.from_iterable(
                [
                    database.get_sessions_for_repository(db, repository)
                    for repository in [
                        r.repository_name
                        for r in db_user.repositories
                        if r.role == RepositoryUserRole.MANAGER
                    ]
                ]
            )
        )
    )


@router.post(
    "/", response_model=AdvancedSessionResponse, responses=AUTHENTICATION_RESPONSES
)
def request_session(
    body: PostSessionRequest, db: Session = Depends(get_db), token=Depends(JWTBearer())
):

    rdp_password = generate_password(length=64)

    owner = get_username(token)

    log.info("Starting session creation for user %s", owner)

    guacamole_username = generate_password()
    guacamole_password = generate_password(length=64)

    guacamole_token = guacamole.get_admin_token()
    guacamole.create_user(guacamole_token, guacamole_username, guacamole_password)

    existing_user_sessions = database.get_sessions_for_user(db, owner)

    if body.type == WorkspaceType.PERSISTENT:
        body.repository = ""
        if WorkspaceType.PERSISTENT in [
            session.type for session in existing_user_sessions
        ]:
            raise HTTPException(
                status_code=404,
                detail={
                    "err_code": "existing_session",
                    "reason": "You already have a open Persistent Session. Please navigate to 'Active Sessions' to Reconnect",
                },
            )
        user = users.get_user(db, owner)
        if user.role == users_models.Role.ADMIN:
            repositories = [
                repo.name for repo in repositories_crud.get_all_projects(db)
            ]
        else:
            repositories = [repo.repository_name for repo in user.repositories]
        session = OPERATOR.start_persistent_session(
            username=get_username(token),
            password=rdp_password,
            repositories=repositories,
        )

    elif body.type == WorkspaceType.READONLY:
        if body.repository in [
            session.repository for session in existing_user_sessions
        ]:
            raise HTTPException(
                status_code=404,
                detail={
                    "err_code": "existing_session",
                    "reason": f"You already have a open Read-Only Session for the repository {body.repository}. Please navigate to 'Active Sessions' to Reconnect",
                },
            )
        verify_project_role(repository=body.repository, token=token, db=db)
        git_model = git_models_crud.get_primary_model_of_repository(db, body.repository)
        if not git_model:
            raise HTTPException(
                status_code=404,
                detail={
                    "err_code": "git_model_not_found",
                    "reason": "The Model has no connected Git Model. Please contact a project manager or admininistrator",
                },
            )
        session = OPERATOR.start_readonly_session(
            password=rdp_password,
            git_url=git_model.path,
            git_revision=git_model.revision,
            entrypoint=git_model.entrypoint,
            git_username=git_model.username,
            git_password=git_model.password,
        )

    guacamole_identifier = guacamole.create_connection(
        guacamole_token,
        rdp_password,
        session["host"],
        list(session["ports"])[0],
    )["identifier"]

    guacamole.assign_user_to_connection(
        guacamole_token, guacamole_username, guacamole_identifier
    )

    database_model = DatabaseSession(
        guacamole_username=guacamole_username,
        guacamole_password=guacamole_password,
        rdp_password=rdp_password,
        guacamole_connection_id=guacamole_identifier,
        owner_name=owner,
        **body.dict(),
        **session,
    )
    response = database.create_session(db=db, session=database_model).__dict__
    response["owner"] = response["owner_name"]
    response["state"] = OPERATOR.get_session_state(response["id"])
    response["rdp_password"] = rdp_password
    response["guacamole_password"] = guacamole_password
    response["last_seen"] = get_last_seen(database_model.id)
    return response


@router.delete("/{id}/", status_code=204, responses=AUTHENTICATION_RESPONSES)
def end_session(id: str, db: Session = Depends(get_db), token=Depends(JWTBearer())):
    s = sessions.get_session_by_id(db, id)
    if s.owner_name != get_username(token) and verify_project_role(
        repository=s.repository,
        token=token,
        db=db,
        allowed_roles=["manager", "administrator"],
    ):
        raise HTTPException(
            status_code=403,
            detail="The owner of the repository does not match with your username. You have to be administrator or manager to delete other sessions.",
        )
    database.delete_session(db, id)
    OPERATOR.kill_session(id)


@router.get(
    "/usage",
    response_model=GetSessionUsageResponse,
    responses=AUTHENTICATION_RESPONSES,
    dependencies=[Depends(JWTBearer())],
)
def get_session_usage():
    return t4c_manager.get_t4c_status()


@router.post(
    "/{id}/guacamole-tokens",
    response_model=GuacamoleAuthentication,
    responses=AUTHENTICATION_RESPONSES,
)
def create_guacamole_token(
    id: str,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    session = database.get_session_by_id(db, id)
    if session.owner_name != get_username(token):
        raise HTTPException(
            status_code=403,
            detail="The owner of the session does not match with your username.",
        )

    token = guacamole.get_token(session.guacamole_username, session.guacamole_password)
    return GuacamoleAuthentication(
        token=json.dumps(token),
        url=config["extensions"]["guacamole"]["publicURI"] + "/#/",
    )
