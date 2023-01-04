# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import itertools
import json
import logging
import typing as t

from fastapi import APIRouter, Depends, HTTPException, status
from requests.exceptions import RequestException
from sqlalchemy.orm import Session

from capellacollab.config import config
from capellacollab.core.authentication.database import (
    ProjectRoleVerification,
    RoleVerification,
)
from capellacollab.core.authentication.helper import get_username
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.credentials import generate_password
from capellacollab.core.database import get_db
from capellacollab.core.models import Message
from capellacollab.projects.models import DatabaseProject
from capellacollab.projects.toolmodels.injectables import (
    get_existing_capella_model,
    get_existing_project,
)
from capellacollab.projects.toolmodels.models import DatabaseCapellaModel
from capellacollab.projects.toolmodels.modelsources.git.models import (
    DatabaseGitModel,
)
from capellacollab.projects.users.crud import ProjectUserRole
from capellacollab.sessions import crud, guacamole
from capellacollab.sessions.files import routes as files
from capellacollab.sessions.models import DatabaseSession
from capellacollab.sessions.operators import get_operator
from capellacollab.sessions.operators.k8s import KubernetesOperator
from capellacollab.sessions.schema import (
    GetSessionsResponse,
    GuacamoleAuthentication,
    PostPersistentSessionRequest,
    PostReadonlySessionEntry,
    PostReadonlySessionRequest,
    WorkspaceType,
)
from capellacollab.sessions.sessions import inject_attrs_in_sessions
from capellacollab.settings.integrations.purevariants.crud import (
    get_pure_variants_configuration,
)
from capellacollab.settings.modelsources.t4c.repositories.crud import (
    get_user_t4c_repositories,
)
from capellacollab.settings.modelsources.t4c.repositories.interface import (
    add_user_to_repository,
)
from capellacollab.tools.crud import (
    get_image_for_tool_version,
    get_readonly_image_for_version,
    get_tool_by_name,
    get_version_by_name,
)
from capellacollab.tools.injectables import (
    get_exisiting_tool_version,
    get_existing_tool,
)
from capellacollab.tools.models import Tool, Version
from capellacollab.users.injectables import get_own_user
from capellacollab.users.models import DatabaseUser, Role

from . import util
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
        return inject_attrs_in_sessions(crud.get_all_sessions(db))

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
                    crud.get_sessions_for_repository(db, project)
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

    if not body.models:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "err_code": "NO_MODELS",
                "reason": "No models have been provided in this request for a read-only session.",
            },
        )

    entries_with_models = [
        (entry, get_existing_capella_model(project.slug, entry.model_slug, db))
        for entry in body.models
    ]

    # Validate git models against the models
    for entry, model in entries_with_models:
        if not any(
            gm for gm in model.git_models if gm.id == entry.git_model_id
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "err_code": "GIT_MODEL_NOT_FOUND",
                    "reason": "The selected model does not have the requested Git repository. Please contact a project manager or administrator",
                },
            )

    model = entries_with_models[0][1]
    if not model.version:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "err_code": "VERSION_NOT_CONFIGURED",
                "reason": f"Model {model.slug} has no tool version configured.",
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
        git_repos_json=list(models_as_json(entries_with_models)),
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


def models_as_json(
    models: t.List[t.Tuple[PostReadonlySessionEntry, DatabaseCapellaModel]]
):
    for entry, model in models:
        git_model = next(
            gm for gm in model.git_models if gm.id == entry.git_model_id
        )
        yield git_model_as_json(git_model, entry.deep_clone)


def git_model_as_json(
    git_model: DatabaseGitModel, deep_clone: bool
) -> dict[str, str | int]:
    d = {
        "url": git_model.path,
        "revision": git_model.revision,
        "depth": 0 if deep_clone else 1,
        "entrypoint": git_model.entrypoint,
        "nature": git_model.model.nature.name,
    }
    if git_model.username:
        d["username"] = git_model.username
        d["password"] = git_model.password
    return d


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

    existing_user_sessions = crud.get_sessions_for_user(db, owner)

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

    if tool.integrations.t4c:
        # When using a different tool with TeamForCapella support (e.g. Capella + pure::variants),
        # the version ID doesn't match the version from the T4C integration.
        # We have to find the matching Capella version by name.
        t4c_repositories = get_user_t4c_repositories(db, version.name, user)

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

    (
        pv_license_server_url,
        pure_variants_secret_name,
        pv_warnings,
    ) = determine_pure_variants_configuration(db, user, tool)
    warnings += pv_warnings

    session = operator.start_persistent_session(
        username=get_username(token),
        password=rdp_password,
        docker_image=docker_image,
        t4c_license_secret=t4c_license_secret,
        t4c_json=t4c_json,
        pure_variants_license_server=pv_license_server_url,
        pure_variants_secret_name=pure_variants_secret_name,
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


def determine_pure_variants_configuration(
    db: Session, user: DatabaseUser, tool: Tool
) -> tuple[str, str, list[str]]:
    warnings = []
    if not tool.integrations.pure_variants:
        return (None, None, warnings)

    if (
        not [
            model
            for association in user.projects
            for model in association.project.models
            if model.restrictions.allow_pure_variants
        ]
        and user.role == Role.USER
    ):
        warnings.append(
            Message(
                reason=(
                    "You are trying to create a persistent session with a pure::variants integration.",
                    "We were not able to find a model with a pure::variants integration.",
                    "Your session will not be connected to the pure::variants license server.",
                )
            )
        )
        return (None, None, warnings)

    if not (pv_license := get_pure_variants_configuration(db)):
        warnings.append(
            Message(
                reason=(
                    "You are trying to create a persistent session with a pure::variants integration.",
                    "We were not able to find a valid license server URL in our database.",
                    "Your session will not be connected to the pure::variants license server.",
                )
            )
        )
        return (None, None, warnings)

    return (pv_license.license_server_url, "pure-variants", warnings)


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
    response = crud.create_session(db=db, session=database_model)
    response.state = "New"
    response.last_seen = "UNKNOWN"
    return response


@router.delete("/{session_id}", status_code=204)
def end_session(
    session: DatabaseSession = Depends(get_existing_session),
    db: Session = Depends(get_db),
    operator: KubernetesOperator = Depends(get_operator),
):
    util.terminate_session(db, session, operator)


@router.post(
    "/{id}/guacamole-tokens",
    response_model=GuacamoleAuthentication,
)
def create_guacamole_token(
    id: str,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    session = crud.get_session_by_id(db, id)
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


router.include_router(router=files.router, prefix="/{session_id}/files")
