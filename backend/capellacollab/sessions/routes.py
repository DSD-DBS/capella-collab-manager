# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import itertools
import json
import logging
import typing as t

import requests
from fastapi import APIRouter, Depends, HTTPException, status
from requests.exceptions import RequestException
from sqlalchemy.orm import Session

import capellacollab.projects.capellamodels.modelsources.git.crud as git_models_crud
from capellacollab.config import config
from capellacollab.core.authentication.database import (
    ProjectRoleVerification,
    RoleVerification,
    verify_project_role,
)
from capellacollab.core.authentication.helper import get_username
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.credentials import generate_password
from capellacollab.core.database import get_db
from capellacollab.core.models import Message
from capellacollab.projects.capellamodels.injectables import (
    get_existing_capella_model,
    get_existing_project,
)
from capellacollab.projects.capellamodels.models import DatabaseCapellaModel
from capellacollab.projects.capellamodels.modelsources.git.models import (
    DatabaseGitModel,
)
from capellacollab.projects.models import DatabaseProject
from capellacollab.projects.users.crud import ProjectUserRole
from capellacollab.sessions import database, guacamole
from capellacollab.sessions.files import routes as files
from capellacollab.sessions.models import DatabaseSession
from capellacollab.sessions.operators import get_operator
from capellacollab.sessions.operators.k8s import KubernetesOperator
from capellacollab.sessions.schema import (
    DepthType,
    GetSessionsResponse,
    GuacamoleAuthentication,
    PostPersistentSessionRequest,
    PostReadonlySessionRequest,
    WorkspaceType,
)
from capellacollab.sessions.sessions import inject_attrs_in_sessions
from capellacollab.settings.integrations.purevariants.crud import get_license
from capellacollab.settings.modelsources.t4c.repositories.crud import (
    get_user_t4c_repositories,
)
from capellacollab.settings.modelsources.t4c.repositories.interface import (
    add_user_to_repository,
    remove_user_from_repository,
)
from capellacollab.tools.crud import (
    get_image_for_tool_version,
    get_readonly_image_for_version,
)
from capellacollab.tools.injectables import (
    get_exisiting_tool_version,
    get_existing_tool,
)
from capellacollab.tools.models import Tool, Version
from capellacollab.users.injectables import get_own_user
from capellacollab.users.models import DatabaseUser, Role

from .injectables import get_existing_session

router = APIRouter(
    dependencies=[Depends(RoleVerification(required_role=Role.USER))]
)

project_router = APIRouter(
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


@project_router.post(
    "/readonly",
    response_model=GetSessionsResponse,
    dependencies=[
        Depends(ProjectRoleVerification(required_role=ProjectUserRole.USER))
    ],
)
def request_session(
    body: PostReadonlySessionRequest,
    db_user: DatabaseUser = Depends(get_own_user),
    project: DatabaseProject = Depends(get_existing_project),
    operator: KubernetesOperator = Depends(get_operator),
    db: Session = Depends(get_db),
):
    log.info("Starting persistent session creation for user %s", db_user.name)

    model = get_existing_capella_model(project.slug, body.model_slug, db)
    models = [
        m
        for m in project.models
        if m.git_models and m.version.id == model.version.id
    ]
    if not models:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "err_code": "GIT_MODEL_NOT_FOUND",
                "reason": "The selected model has no connected Git repository. Please contact a project manager or administrator",
            },
        )

    docker_image = get_readonly_image_for_version(model.version)
    if not docker_image:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "err_code": "IMAGE_NOT_FOUND",
                "reason": "The tool has no read-only support. Please contact an admininistrator",
            },
        )

    rdp_password = generate_password(length=64)

    session = operator.start_readonly_session(
        password=rdp_password,
        docker_image=docker_image,
        git_repos_json=list(models_as_json(models, model.version)),
    )

    return create_database_and_guacamole_session(
        db,
        WorkspaceType.READONLY,
        session,
        db_user.name,
        rdp_password,
        model.tool,
        model.version,
        project,
        None,
    )


def models_as_json(models: t.List[DatabaseCapellaModel], version: Version):
    for model in models:
        for git_model in model.git_models:
            yield git_model_as_json(git_model)


def git_model_as_json(git_model: DatabaseGitModel) -> dict[str, str | int]:
    json = {
        "url": git_model.path,
        "revision": git_model.revision,
        "depth": 1,
        "entrypoint": git_model.entrypoint,
        "nature": git_model.model.nature.name,
    }
    if git_model.username:
        json["username"] = git_model.username
        json["password"] = git_model.password
    return json


@router.post("/persistent", response_model=GetSessionsResponse)
def request_persistent_session(
    body: PostPersistentSessionRequest,
    user: DatabaseUser = Depends(get_own_user),
    db: Session = Depends(get_db),
    operator: KubernetesOperator = Depends(get_operator),
    token=Depends(JWTBearer()),
):
    warnings: list[Message] = []
    rdp_password = generate_password(length=64)

    owner = get_username(token)

    log.info("Starting persistent session for user %s", owner)

    existing_user_sessions = database.get_sessions_for_user(db, owner)

    if WorkspaceType.PERSISTENT in [
        session.type for session in existing_user_sessions
    ]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "err_code": "EXISTING_SESSION",
                "reason": "You already have a open persistent session. Please navigate to 'Active Sessions' to connect",
            },
        )

    tool = get_existing_tool(body.tool_id, db)
    version = get_exisiting_tool_version(tool.id, body.version_id, db)

    docker_image = get_image_for_tool_version(db, version.id)

    t4c_password = None
    t4c_json = None
    t4c_license_secret = None
    if tool.name == "Capella":
        t4c_repositories = (
            get_user_t4c_repositories(db, tool, version, user)
            if tool.name == "Capella"
            else None
        )

        t4c_json = [
            {
                "repository": repository.name,
                "protocol": repository.instance.protocol,
                "port": repository.instance.port,
                "host": repository.instance.host,
                "instance": repository.instance.name,
            }
            for repository in t4c_repositories
        ]

        t4c_license_secret = (
            t4c_repositories[0].instance.license if t4c_repositories else None
        )

        t4c_password = generate_password()
        for repository in t4c_repositories:
            try:
                add_user_to_repository(
                    repository.instance,
                    repository.name,
                    username=owner,
                    password=t4c_password,
                    is_admin=RoleVerification(
                        required_role=Role.ADMIN, verify=False
                    )(token, db),
                )
            except RequestException:
                warnings.append(
                    Message(
                        reason=(
                            f"The creation of your user in the repository '{repository.name}' of the the instance '{repository.instance.name}' failed.",
                            "Most likely this is due to a downtime of the corresponding TeamForCapella server.",
                            "If you don't need access to the repository you can still use the session.",
                        )
                    )
                )
                log.warning(
                    "Could not add user to t4c repository '%s' of instance '%s'",
                    repository.name,
                    repository.instance.name,
                    exc_info=True,
                )

    session = operator.start_persistent_session(
        username=get_username(token),
        password=rdp_password,
        docker_image=docker_image,
        t4c_license_secret=t4c_license_secret,
        t4c_json=t4c_json,
        pure_variants_license_server=get_license(db) or "UNSET",
    )

    response = create_database_and_guacamole_session(
        db,
        WorkspaceType.PERSISTENT,
        session,
        owner,
        rdp_password,
        tool,
        version,
        None,
        t4c_password,
    )
    response.warnings = warnings
    return response


def create_database_and_guacamole_session(
    db: Session,
    type: WorkspaceType,
    session: dict[str, t.Any],
    owner: str,
    rdp_password: str,
    tool: Tool,
    version: Version,
    project,
    t4c_password: t.Optional[str] = None,
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
        project=project,
        type=type,
        t4c_password=t4c_password,
        tool=tool,
        version=version,
        **session,
    )
    response = database.create_session(db=db, session=database_model)
    response.state = "New"
    response.last_seen = "UNKNOWN"
    return response


@router.delete("/{session_id}", status_code=204)
def end_session(
    session: DatabaseSession = Depends(get_existing_session),
    db: Session = Depends(get_db),
    operator: KubernetesOperator = Depends(get_operator),
):
    if (
        session.tool.name == "Capella"
        and session.type == WorkspaceType.PERSISTENT
    ):
        for repository in get_user_t4c_repositories(
            db, session.tool, session.version, session.owner
        ):
            try:
                remove_user_from_repository(
                    repository.instance,
                    repository.name,
                    username=session.owner.name,
                )
            except RequestException:
                log.exception(
                    "Could not delete user from repository '%s' of instance '%s'. Please delete the user manually.",
                    exc_info=True,
                )

    database.delete_session(db, session)
    operator.kill_session(session.id)


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
