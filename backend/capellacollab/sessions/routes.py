# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import itertools
import json
import logging
import typing as t

from fastapi import APIRouter, Depends, HTTPException, status
from requests.exceptions import RequestException
from sqlalchemy.orm import Session

from capellacollab.config import config
from capellacollab.core import models as core_models
from capellacollab.core.authentication import helper as auth_helper
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.credentials import generate_password
from capellacollab.core.database import get_db
from capellacollab.projects.models import DatabaseProject
from capellacollab.projects.toolmodels import (
    injectables as toolmodels_injectables,
)
from capellacollab.projects.toolmodels.models import DatabaseCapellaModel
from capellacollab.projects.toolmodels.modelsources.git import (
    models as git_models,
)
from capellacollab.projects.users.crud import ProjectUserRole
from capellacollab.sessions import crud, guacamole, schema
from capellacollab.sessions.files import routes as files
from capellacollab.sessions.models import DatabaseSession
from capellacollab.sessions.operators import get_operator
from capellacollab.sessions.operators.k8s import KubernetesOperator
from capellacollab.sessions.sessions import inject_attrs_in_sessions
from capellacollab.settings.integrations.purevariants import (
    crud as purevariants_crud,
)
from capellacollab.settings.modelsources.t4c.repositories import (
    crud as repo_crud,
)
from capellacollab.settings.modelsources.t4c.repositories import (
    interface as repo_interface,
)
from capellacollab.tools import crud as tools_crud
from capellacollab.tools import injectables as tools_injectables
from capellacollab.tools import models as tools_models
from capellacollab.users import injectables as users_injectables
from capellacollab.users import models as users_models

from . import injectables, util

router = APIRouter(
    dependencies=[
        Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.USER
            )
        )
    ]
)

project_router = APIRouter(
    dependencies=[
        Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.USER
            )
        )
    ]
)

users_router = APIRouter(
    dependencies=[
        Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.USER
            )
        )
    ]
)

log = logging.getLogger(__name__)


@router.get("/", response_model=list[schema.GetSessionsResponse])
def get_current_sessions(
    db_user: users_models.DatabaseUser = Depends(
        users_injectables.get_own_user
    ),
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    if auth_injectables.RoleVerification(
        required_role=users_models.Role.ADMIN, verify=False
    )(token, db):
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
    response_model=schema.GetSessionsResponse,
    dependencies=[
        Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=ProjectUserRole.USER
            )
        )
    ],
)
def request_session(
    body: schema.PostReadonlySessionRequest,
    db_user: users_models.DatabaseUser = Depends(
        users_injectables.get_own_user
    ),
    project: DatabaseProject = Depends(
        toolmodels_injectables.get_existing_project
    ),
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
        (
            entry,
            toolmodels_injectables.get_existing_capella_model(
                project.slug, entry.model_slug, db
            ),
        )
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

    if crud.get_session_by_user_project_version(
        db, db_user, project, model.version
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "err_code": "EXISTING_SESSION",
                "reason": f"You already have a read-only session for {project.name}/{model.tool.name} and tool {model.tool.name}/{model.version.name}. Close the existing session before starting a new one.",
            },
        )

    docker_image = tools_crud.get_readonly_image_for_version(model.version)
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
        username=db_user.name,
        tool_name=model.tool.name,
        version_name=model.version.name,
        password=rdp_password,
        docker_image=docker_image,
        git_repos_json=list(models_as_json(entries_with_models)),
    )

    return create_database_and_guacamole_session(
        db,
        schema.WorkspaceType.READONLY,
        session,
        db_user.name,
        rdp_password,
        model.tool,
        model.version,
        project,
        None,
    )


def models_as_json(
    models: list[tuple[schema.PostReadonlySessionEntry, DatabaseCapellaModel]]
):
    for entry, model in models:
        if not (
            git_model := next(
                (gm for gm in model.git_models if gm.id == entry.git_model_id),
                None,
            )
        ):
            continue
        yield git_model_as_json(git_model, entry.deep_clone)


def git_model_as_json(
    git_model: git_models.DatabaseGitModel, deep_clone: bool
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


@router.post("/persistent", response_model=schema.GetSessionsResponse)
def request_persistent_session(
    body: schema.PostPersistentSessionRequest,
    user: users_models.DatabaseUser = Depends(users_injectables.get_own_user),
    db: Session = Depends(get_db),
    operator: KubernetesOperator = Depends(get_operator),
    token=Depends(JWTBearer()),
):
    owner = auth_helper.get_username(token)

    log.info("Starting persistent session for user %s", owner)

    existing_user_sessions = crud.get_sessions_for_user(db, owner)

    if schema.WorkspaceType.PERSISTENT in [
        session.type for session in existing_user_sessions
    ]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "err_code": "EXISTING_SESSION",
                "reason": "You already have a open persistent session. Please navigate to 'Active Sessions' to connect",
            },
        )

    tool = tools_injectables.get_existing_tool(body.tool_id, db)
    version = tools_injectables.get_exisiting_tool_version(
        tool.id, body.version_id, db
    )

    if tool.integrations and tool.integrations.jupyter:
        response = start_persistent_jupyter_session(
            db=db,
            operator=operator,
            owner=owner,
            token=token,
            tool=tool,
            version=version,
        )
    else:
        response = start_persistent_guacamole_session(
            db=db,
            operator=operator,
            user=user,
            owner=owner,
            token=token,
            tool=tool,
            version=version,
        )

    return response


def start_persistent_jupyter_session(
    db: Session,
    operator: KubernetesOperator,
    owner: str,
    token: str,
    tool: tools_models.Tool,
    version: tools_models.Version,
):
    docker_image = tools_crud.get_image_for_tool_version(db, version.id)
    jupyter_token = generate_password(length=64)

    session = operator.start_persistent_jupyter_session(
        username=auth_helper.get_username(token),
        tool_name=tool.name,
        version_name=version.name,
        token=jupyter_token,
        docker_image=docker_image,
    )

    return create_database_session(
        db,
        schema.WorkspaceType.PERSISTENT,
        session,
        owner,
        tool,
        version,
        None,
        jupyter_token=jupyter_token,
    )


def start_persistent_guacamole_session(
    db: Session,
    operator: KubernetesOperator,
    user: users_models.DatabaseUser,
    owner: str,
    token: str,
    tool: tools_models.Tool,
    version: tools_models.Version,
):
    warnings: list[core_models.Message] = []
    t4c_password = None
    t4c_json = None
    t4c_license_secret = None

    if tool.integrations.t4c:
        # When using a different tool with TeamForCapella support (e.g. Capella + pure::variants),
        # the version ID doesn't match the version from the T4C integration.
        # We have to find the matching Capella version by name.
        t4c_repositories = repo_crud.get_user_t4c_repositories(
            db, version.name, user
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
                repo_interface.add_user_to_repository(
                    repository.instance,
                    repository.name,
                    username=owner,
                    password=t4c_password,
                    is_admin=auth_injectables.RoleVerification(
                        required_role=users_models.Role.ADMIN, verify=False
                    )(token, db),
                )
            except RequestException:
                warnings.append(
                    core_models.Message(
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

    docker_image = tools_crud.get_image_for_tool_version(db, version.id)
    rdp_password = generate_password(length=64)

    session = operator.start_persistent_capella_session(
        username=auth_helper.get_username(token),
        tool_name=tool.name,
        version_name=version.name,
        password=rdp_password,
        docker_image=docker_image,
        t4c_license_secret=t4c_license_secret,
        t4c_json=t4c_json,
        pure_variants_license_server=pv_license_server_url,
        pure_variants_secret_name=pure_variants_secret_name,
    )

    response = create_database_and_guacamole_session(
        db,
        schema.WorkspaceType.PERSISTENT,
        session,
        owner,
        rdp_password,
        tool,
        version,
        None,
        t4c_password,
    )
    response.warnings += warnings
    response.warnings += pv_warnings
    return response


def determine_pure_variants_configuration(
    db: Session, user: users_models.DatabaseUser, tool: tools_models.Tool
) -> tuple[str | None, str | None, list[core_models.Message]]:
    warnings: list[core_models.Message] = []
    if not tool.integrations.pure_variants:
        return (None, None, warnings)

    if (
        not [
            model
            for association in user.projects
            for model in association.project.models
            if model.restrictions.allow_pure_variants
        ]
        and user.role == users_models.Role.USER
    ):
        warnings.append(
            core_models.Message(
                reason=(
                    "You are trying to create a persistent session with a pure::variants integration.",
                    "We were not able to find a model with a pure::variants integration.",
                    "Your session will not be connected to the pure::variants license server.",
                )
            )
        )
        return (None, None, warnings)

    if not (
        pv_license := purevariants_crud.get_pure_variants_configuration(db)
    ):
        warnings.append(
            core_models.Message(
                reason=(
                    "You are trying to create a persistent session with a pure::variants integration.",
                    "We were not able to find a valid license server URL in our database.",
                    "Your session will not be connected to the pure::variants license server.",
                )
            )
        )
        return (None, None, warnings)

    return (pv_license.license_server_url, "pure-variants", warnings)


def create_database_session(
    db: Session,
    type: schema.WorkspaceType,
    session: dict[str, t.Any],
    owner: str,
    tool: tools_models.Tool,
    version: tools_models.Version,
    project: DatabaseProject | None,
    **kwargs,
) -> DatabaseSession:
    database_model = DatabaseSession(
        tool=tool,
        version=version,
        owner_name=owner,
        project=project,
        type=type,
        **session,
        **kwargs,
    )
    response = crud.create_session(db=db, session=database_model)
    response.state = "New"
    response.last_seen = "UNKNOWN"
    response.warnings = []
    return response


def create_database_and_guacamole_session(
    db: Session,
    type: schema.WorkspaceType,
    session: dict[str, t.Any],
    owner: str,
    rdp_password: str,
    tool: tools_models.Tool,
    version: tools_models.Version,
    project: DatabaseProject | None,
    t4c_password: str | None = None,
) -> DatabaseSession:
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

    return create_database_session(
        db,
        type,
        session,
        owner,
        tool,
        version,
        project,
        t4c_password=t4c_password,
        rdp_password=rdp_password,
        guacamole_username=guacamole_username,
        guacamole_password=guacamole_password,
        guacamole_connection_id=guacamole_identifier,
    )


@router.delete("/{session_id}", status_code=204)
def end_session(
    session: DatabaseSession = Depends(injectables.get_existing_session),
    db: Session = Depends(get_db),
    operator: KubernetesOperator = Depends(get_operator),
):
    util.terminate_session(db, session, operator)


@router.post(
    "/{session_id}/guacamole-tokens",
    response_model=schema.GuacamoleAuthentication,
)
def create_guacamole_token(
    session: DatabaseSession = Depends(injectables.get_existing_session),
    token=Depends(JWTBearer()),
):
    if session.owner_name != auth_helper.get_username(token):
        raise HTTPException(
            status_code=403,
            detail={
                "reason": "The owner of the session does not match with your username."
            },
        )

    token = guacamole.get_token(
        session.guacamole_username, session.guacamole_password
    )
    return schema.GuacamoleAuthentication(
        token=json.dumps(token),
        url=config["extensions"]["guacamole"]["publicURI"] + "/#/",
    )


router.include_router(router=files.router, prefix="/{session_id}/files")


@users_router.get(
    "/{user_id}/sessions", response_model=list[schema.OwnSessionResponse]
)
def get_sessions_for_user(
    user: users_models.DatabaseUser = Depends(
        users_injectables.get_existing_user
    ),
    current_user: users_models.DatabaseUser = Depends(
        users_injectables.get_own_user
    ),
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    if user != current_user and not auth_injectables.RoleVerification(
        required_role=users_models.Role.ADMIN, verify=False
    )(token, db):
        raise HTTPException(
            status_code=403,
            detail={
                "reason": "You can only see your own sessions.",
                "technical": "If you are a project lead or administrator, please use the /sessions endpoint",
            },
        )

    return inject_attrs_in_sessions(user.sessions)
