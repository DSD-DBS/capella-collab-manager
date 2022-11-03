# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import itertools
import json
import logging
import typing as t

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

import capellacollab.projects.capellamodels.modelsources.git.crud as git_models_crud
import capellacollab.projects.capellamodels.modelsources.t4c.connection as t4c_manager
import capellacollab.users.crud as users
from capellacollab.config import config
from capellacollab.core.authentication.database import (
    RoleVerification,
    verify_project_role,
)
from capellacollab.core.authentication.helper import get_username
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.credentials import generate_password
from capellacollab.core.database import get_db
from capellacollab.projects.capellamodels.models import DatabaseCapellaModel
from capellacollab.projects.capellamodels.modelsources.t4c.models import (
    DatabaseT4CModel,
)
from capellacollab.projects.models import DatabaseProject
from capellacollab.projects.users.crud import ProjectUserRole
from capellacollab.projects.users.models import (
    ProjectUserAssociation,
    ProjectUserPermission,
)
from capellacollab.sessions import database, guacamole
from capellacollab.sessions.files import routes as files
from capellacollab.sessions.models import DatabaseSession
from capellacollab.sessions.operators import Operator, get_operator
from capellacollab.sessions.schema import (
    AdvancedSessionResponse,
    DepthType,
    GetSessionsResponse,
    GetSessionUsageResponse,
    GuacamoleAuthentication,
    PostPersistentSessionRequest,
    PostSessionRequest,
    WorkspaceType,
)
from capellacollab.sessions.sessions import inject_attrs_in_sessions
from capellacollab.settings.modelsources.t4c.repositories.models import (
    DatabaseT4CRepository,
)
from capellacollab.tools.crud import get_image_for_tool_version
from capellacollab.tools.injectables import (
    get_exisiting_tool_version,
    get_existing_tool,
)
from capellacollab.tools.models import Tool, Version
from capellacollab.users.injectables import get_own_user
from capellacollab.users.models import DatabaseUser, Role

router = APIRouter(
    dependencies=[Depends(RoleVerification(required_role=Role.USER))]
)
log = logging.getLogger(__name__)


@router.get("/", response_model=t.List[GetSessionsResponse])
def get_current_sessions(
    db_user: DatabaseUser = Depends(get_own_user),
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    if RoleVerification(required_role=Role.ADMIN, verify=False)(token, db):
        return inject_attrs_in_sessions(database.get_all_sessions(db))

    if not any(
        project_user.role == ProjectUserRole.MANAGER
        for project_user in db_user.projects
    ):
        raise HTTPException(
            status_code=403,
            detail={
                "reason": "You have to be project lead for at least one repository.",
            },
        )
    return inject_attrs_in_sessions(
        list(
            itertools.chain.from_iterable(
                [
                    database.get_sessions_for_repository(db, project)
                    for project in [
                        p.name
                        for p in db_user.projects
                        if p.role == ProjectUserRole.MANAGER
                    ]
                ]
            )
        ),
    )


@router.post(
    "/",
    response_model=AdvancedSessionResponse,
)
def request_session(
    body: PostSessionRequest,
    db_user: DatabaseUser = Depends(get_own_user),
    operator: Operator = Depends(get_operator),
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    assert body.type == WorkspaceType.READONLY

    rdp_password = generate_password(length=64)

    owner = db_user.username

    log.info("Starting persistent session creation for user %s", owner)

    existing_user_sessions = database.get_sessions_for_user(db, owner)

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
    git_model = git_models_crud.get_primary_model_of_repository(
        db, body.repository
    )
    if not git_model:
        raise HTTPException(
            status_code=404,
            detail={
                "err_code": "git_model_not_found",
                "reason": "The Model has no connected Git Model. Please contact a project manager or admininistrator",
            },
        )

    revision = body.branch or git_model.revision
    if body.depth == DepthType.LatestCommit:
        depth = 1
    elif body.depth == DepthType.CompleteHistory:
        depth = 0
    else:
        raise HTTPException(
            status_code=400,
            detail={
                "err_code": "wrong_depth_format",
                "reason": f"Depth type {depth} is not allowed.",
            },
        )
    session = operator.start_readonly_session(
        password=rdp_password,
        git_url=git_model.path,
        git_revision=revision,
        entrypoint=git_model.entrypoint,
        git_username=git_model.username,
        git_password=git_model.password,
        git_depth=depth,
    )

    return create_database_and_guacamole_session(
        WorkspaceType.READONLY,
        session,
        owner,
        rdp_password,
        db,
        repository=body.repository,
    )


@router.post("/persistent", response_model=AdvancedSessionResponse)
def request_persistent_session(
    body: PostPersistentSessionRequest,
    user: DatabaseUser = Depends(get_own_user),
    db: Session = Depends(get_db),
    operator: Operator = Depends(get_operator),
    token=Depends(JWTBearer()),
):
    rdp_password = generate_password(length=64)

    owner = get_username(token)

    log.info("Starting persistent session for user %s", owner)

    existing_user_sessions = database.get_sessions_for_user(db, owner)

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

    tool = get_existing_tool(body.tool_id, db)
    version = get_exisiting_tool_version(tool.id, body.version_id, db)

    docker_image = get_image_for_tool_version(db, version.id)

    admin_stmt = (
        select(DatabaseT4CRepository)
        .join(DatabaseT4CRepository.models)
        .join(DatabaseT4CModel.model)
        .where(DatabaseCapellaModel.tool == tool)
        .where(DatabaseCapellaModel.version == version)
    )

    stmt = (
        admin_stmt.join(DatabaseCapellaModel.project)
        .join(DatabaseProject.users)
        .where(
            ProjectUserAssociation.permission == ProjectUserPermission.WRITE
        )
        .where(ProjectUserAssociation.user == user)
    )

    t4c_repositories: t.Optional[list[DatabaseT4CRepository]] = (
        (
            db.execute(admin_stmt if user.role == Role.ADMIN else stmt)
            .scalars()
            .all()
        )
        if tool.name == "Capella"
        else None
    )

    t4c_json = [
        {
            "repository": repository.name,
            "port": repository.instance.port,
            "host": repository.instance.host,
            "instance": repository.instance.name,
        }
        for repository in t4c_repositories
    ]

    t4c_license_secret = (
        t4c_repositories[0].instance.license if t4c_repositories else None
    )

    session = operator.start_persistent_session(
        username=get_username(token),
        password=rdp_password,
        docker_image=docker_image,
        t4c_license_secret=t4c_license_secret,
        t4c_json=t4c_json,
    )

    return create_database_and_guacamole_session(
        WorkspaceType.PERSISTENT, session, owner, rdp_password, db
    )


def create_database_and_guacamole_session(
    type: WorkspaceType, session, owner, rdp_password, db, repository=""
):
    guacamole_username = generate_password()
    guacamole_password = generate_password(length=64)

    guacamole_token = guacamole.get_admin_token()
    guacamole.create_user(
        guacamole_token, guacamole_username, guacamole_password
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
        repository=repository,
        type=type,
        **session,
    )
    response = database.create_session(db=db, session=database_model).__dict__
    response["owner"] = response["owner_name"]
    response["state"] = "New"
    response["rdp_password"] = rdp_password
    response["guacamole_password"] = guacamole_password
    response["last_seen"] = "UNKNOWN"
    return response


@router.delete("/{id}", status_code=204)
def end_session(
    id: str,
    db: Session = Depends(get_db),
    operator: Operator = Depends(get_operator),
    token=Depends(JWTBearer()),
):
    s = database.get_session_by_id(db, id)
    if s.owner_name != get_username(token) and verify_project_role(
        repository=s.repository,
        token=token,
        db=db,
        allowed_roles=["manager", "administrator"],
    ):
        raise HTTPException(
            status_code=403,
            detail={
                "reason": "The owner of the repository does not match with your username. You have to be administrator or manager to delete other sessions."
            },
        )
    database.delete_session(db, id)
    operator.kill_session(id)
    return None


@router.get(
    "/usage",
    response_model=GetSessionUsageResponse,
    dependencies=[Depends(JWTBearer())],
)
def get_session_usage():
    return t4c_manager.get_t4c_status()


@router.post(
    "/{id}/guacamole-tokens",
    response_model=GuacamoleAuthentication,
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
            detail={
                "reason": "The owner of the session does not match with your username."
            },
        )

    token = guacamole.get_token(
        session.guacamole_username, session.guacamole_password
    )
    return GuacamoleAuthentication(
        token=json.dumps(token),
        url=config["extensions"]["guacamole"]["publicURI"] + "/#/",
    )


router.include_router(router=files.router, prefix="/{id}/files")
