# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import itertools
import json
import logging
import typing as t

import fastapi
from fastapi import status
from sqlalchemy import orm

from capellacollab import config
from capellacollab.core import credentials, database
from capellacollab.core import models as core_models
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.core.authentication import jwt_bearer
from capellacollab.projects import injectables as projects_injectables
from capellacollab.projects import models as projects_models
from capellacollab.projects.toolmodels import (
    injectables as toolmodels_injectables,
)
from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.projects.toolmodels.modelsources.git import (
    models as git_models,
)
from capellacollab.projects.users import models as projects_users_models
from capellacollab.sessions import hooks
from capellacollab.sessions.files import routes as files_routes
from capellacollab.tools import crud as tools_crud
from capellacollab.tools import injectables as tools_injectables
from capellacollab.tools import models as tools_models
from capellacollab.users import injectables as users_injectables
from capellacollab.users import models as users_models

from . import (
    crud,
    guacamole,
    injectables,
    models,
    operators,
    sessions,
    util,
    workspace,
)
from .operators import k8s

router = fastapi.APIRouter(
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.USER
            )
        )
    ]
)

project_router = fastapi.APIRouter(
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.USER
            )
        )
    ]
)

users_router = fastapi.APIRouter(
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.USER
            )
        )
    ]
)

log = logging.getLogger(__name__)


@router.get("", response_model=list[models.GetSessionsResponse])
def get_current_sessions(
    db_user: users_models.DatabaseUser = fastapi.Depends(
        users_injectables.get_own_user
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
    token=fastapi.Depends(jwt_bearer.JWTBearer()),
):
    if auth_injectables.RoleVerification(
        required_role=users_models.Role.ADMIN, verify=False
    )(token, db):
        return sessions.inject_attrs_in_sessions(crud.get_sessions(db))

    if not any(
        project_user.role == projects_users_models.ProjectUserRole.MANAGER
        for project_user in db_user.projects
    ):
        raise fastapi.HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "reason": "You have to be project lead for at least one repository.",
            },
        )
    return sessions.inject_attrs_in_sessions(
        list(
            itertools.chain.from_iterable(
                [
                    crud.get_sessions_for_project(db, project)
                    for project in [
                        p.project
                        for p in db_user.projects
                        if p.role
                        == projects_users_models.ProjectUserRole.MANAGER
                    ]
                ]
            )
        ),
    )


@project_router.post(
    "/readonly",
    response_model=models.GetSessionsResponse,
    dependencies=[
        fastapi.Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=projects_users_models.ProjectUserRole.USER
            )
        )
    ],
)
def request_readonly_session(
    body: models.PostReadonlySessionRequest,
    db_user: users_models.DatabaseUser = fastapi.Depends(
        users_injectables.get_own_user
    ),
    project: projects_models.DatabaseProject = fastapi.Depends(
        projects_injectables.get_existing_project
    ),
    operator: k8s.KubernetesOperator = fastapi.Depends(operators.get_operator),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    log.info("Starting read-only session creation for user %s", db_user.name)

    if not body.models:
        raise fastapi.HTTPException(
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
                entry.model_slug, project, db
            ),
        )
        for entry in body.models
    ]

    # Validate git models against the models
    for entry, model in entries_with_models:
        if not any(
            gm for gm in model.git_models if gm.id == entry.git_model_id
        ):
            raise fastapi.HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "err_code": "GIT_MODEL_NOT_FOUND",
                    "reason": "The selected model does not have the requested Git repository. Please contact a project manager or administrator",
                },
            )

    model = entries_with_models[0][1]
    if not model.version:
        raise fastapi.HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "err_code": "VERSION_NOT_CONFIGURED",
                "reason": f"Model {model.slug} has no tool version configured.",
            },
        )

    if crud.exist_readonly_session_for_user_project_version(
        db, db_user, project, model.version
    ):
        raise fastapi.HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "err_code": "EXISTING_SESSION",
                "reason": f"You already have a read-only session for {project.name}/{model.tool.name} and tool {model.tool.name}/{model.version.name}. Close the existing session before starting a new one.",
            },
        )

    docker_image = get_readonly_image_for_version(model.version)
    if not docker_image:
        raise fastapi.HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "err_code": "IMAGE_NOT_FOUND",
                "reason": "The tool has no read-only support. Please contact an admininistrator",
            },
        )

    rdp_password = credentials.generate_password(length=64)

    session = operator.start_session(
        image=docker_image,
        username=db_user.name,
        session_type="readonly",
        tool_name=model.tool.name,
        version_name=model.version.name,
        environment={
            "GIT_REPOS_JSON": json.dumps(
                list(models_as_json(entries_with_models))
            ),
            "RMT_PASSWORD": rdp_password,
        },
        ports={"rdp": 3389, "metrics": 9118, "fileservice": 8000},
    )

    return create_database_and_guacamole_session(
        db=db,
        type=models.WorkspaceType.READONLY,
        session=session,
        owner=db_user.name,
        rdp_password=rdp_password,
        tool=model.tool,
        version=model.version,
        project=project,
        environment={},
    )


def models_as_json(
    session_model_list: list[
        tuple[
            models.PostReadonlySessionEntry,
            toolmodels_models.DatabaseCapellaModel,
        ]
    ]
):
    for entry, model in session_model_list:
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


@router.post("/persistent", response_model=models.GetSessionsResponse)
def request_persistent_session(
    body: models.PostPersistentSessionRequest,
    user: users_models.DatabaseUser = fastapi.Depends(
        users_injectables.get_own_user
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
    operator: k8s.KubernetesOperator = fastapi.Depends(operators.get_operator),
    token=fastapi.Depends(jwt_bearer.JWTBearer()),
):
    log.info("Starting persistent session for user %s", user.name)

    tool = tools_injectables.get_existing_tool(body.tool_id, db)
    version = tools_injectables.get_exisiting_tool_version(
        tool.id, body.version_id, db
    )

    raise_if_conflicting_persistent_sessions(tool, user)

    pvc_name = workspace.create_persistent_workspace(operator, user.name)

    environment: dict[str, str] = {}
    warnings: list[core_models.Message] = []

    for hook in hooks.get_activated_integration_hooks(tool):
        hook_env, hook_warnings = hook.configuration_hook(
            db=db, user=user, tool_version=version, tool=tool, token=token
        )
        environment |= hook_env
        warnings += hook_warnings

    if tool.integrations and tool.integrations.jupyter:
        response = start_persistent_jupyter_session(
            db=db,
            operator=operator,
            owner=user.name,
            tool=tool,
            version=version,
            persistent_workspace_claim_name=pvc_name,
            environment=environment,
        )
    else:
        response = start_persistent_guacamole_session(
            db=db,
            operator=operator,
            user=user,
            owner=user.name,
            tool=tool,
            version=version,
            persistent_workspace_claim_name=pvc_name,
            environment=environment,
        )

    for hook in hooks.get_activated_integration_hooks(tool):
        hook.post_session_creation_hook(
            session_id=response.id, operator=operator, user=user
        )

    response.warnings = warnings

    return response


def raise_if_conflicting_persistent_sessions(
    tool: tools_models.DatabaseTool,
    user: users_models.DatabaseUser,
) -> None:
    existing_user_sessions = user.sessions

    # This is a temporary workaround until we can define a proper locking of workspaces
    # Currently, all tools share one workspace. Eclipse based tools lock the workspace.
    # We can only run one Eclipse-based tool at a time.
    # Status tracked in https://github.com/DSD-DBS/capella-collab-manager/issues/847
    if tool.integrations.jupyter:
        # Check if there is already an Jupyter session running.
        if True in [
            session.tool.integrations.jupyter
            for session in existing_user_sessions
        ]:
            raise fastapi.HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "err_code": "EXISTING_SESSION",
                    "reason": "You already have a Jupyter session. Please navigate to 'Active Sessions' to connect.",
                },
            )
    else:
        if models.WorkspaceType.PERSISTENT in [
            session.type
            for session in existing_user_sessions
            if session.tool.name != "Jupyter"
        ]:
            raise fastapi.HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "err_code": "EXISTING_SESSION",
                    "reason": (
                        "You already have a open persistent Eclipse-based session.",
                        "Currently, we can only run one Eclipse-based session at a time.",
                    ),
                },
            )


def start_persistent_jupyter_session(
    db: orm.Session,
    operator: k8s.KubernetesOperator,
    owner: str,
    tool: tools_models.DatabaseTool,
    environment: dict[str, str],
    version: tools_models.DatabaseVersion,
    persistent_workspace_claim_name: str,
):
    docker_image = get_image_for_tool_version(db, version.id)

    session = operator.start_session(
        image=docker_image,
        username=owner,
        session_type="persistent",
        tool_name=tool.name,
        version_name=version.name,
        environment=environment,
        ports={"http": 8888},
        persistent_workspace_claim_name=persistent_workspace_claim_name,
        prometheus_path=f"{environment.get('JUPYTER_BASE_URL')}/metrics",
        prometheus_port=8888,
        limits="low",
    )

    return create_database_session(
        db=db,
        type=models.WorkspaceType.PERSISTENT,
        session=session,
        owner=owner,
        tool=tool,
        version=version,
        project=None,
        environment=environment,
    )


def start_persistent_guacamole_session(
    db: orm.Session,
    operator: k8s.KubernetesOperator,
    user: users_models.DatabaseUser,
    owner: str,
    tool: tools_models.DatabaseTool,
    version: tools_models.DatabaseVersion,
    persistent_workspace_claim_name: str,
    environment: dict[str, str],
):
    docker_image = get_image_for_tool_version(db, version.id)
    rdp_password = credentials.generate_password(length=64)

    environment = environment | {"RMT_PASSWORD": rdp_password}

    session = operator.start_session(
        image=docker_image,
        username=user.name,
        session_type="persistent",
        tool_name=tool.name,
        version_name=version.name,
        environment=environment,
        ports={"rdp": 3389, "metrics": 9118},
        persistent_workspace_claim_name=persistent_workspace_claim_name,
    )

    response = create_database_and_guacamole_session(
        db=db,
        type=models.WorkspaceType.PERSISTENT,
        session=session,
        owner=owner,
        rdp_password=rdp_password,
        tool=tool,
        version=version,
        project=None,
        environment=environment,
    )
    return response


def create_database_session(
    db: orm.Session,
    type: models.WorkspaceType,
    session: dict[str, t.Any],
    owner: str,
    tool: tools_models.DatabaseTool,
    version: tools_models.DatabaseVersion,
    project: projects_models.DatabaseProject | None,
    **kwargs,
) -> models.DatabaseSession:
    database_model = models.DatabaseSession(
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
    db: orm.Session,
    type: models.WorkspaceType,
    session: dict[str, t.Any],
    owner: str,
    rdp_password: str,
    tool: tools_models.DatabaseTool,
    version: tools_models.DatabaseVersion,
    project: projects_models.DatabaseProject | None,
    environment: dict[str, str],
) -> models.DatabaseSession:
    guacamole_username = credentials.generate_password()
    guacamole_password = credentials.generate_password(length=64)

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
        environment=environment,
        rdp_password=rdp_password,
        guacamole_username=guacamole_username,
        guacamole_password=guacamole_password,
        guacamole_connection_id=guacamole_identifier,
    )


@router.delete("/{session_id}", status_code=204)
def end_session(
    db: orm.Session = fastapi.Depends(database.get_db),
    session: models.DatabaseSession = fastapi.Depends(
        injectables.get_existing_session
    ),
    operator: k8s.KubernetesOperator = fastapi.Depends(operators.get_operator),
):
    util.terminate_session(db, session, operator)


@router.post(
    "/{session_id}/guacamole-tokens",
    response_model=models.GuacamoleAuthentication,
)
def create_guacamole_token(
    session: models.DatabaseSession = fastapi.Depends(
        injectables.get_existing_session
    ),
    user: users_models.DatabaseUser = fastapi.Depends(
        users_injectables.get_own_user
    ),
):
    if session.owner_name != user.name:
        raise fastapi.HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "reason": "The owner of the session does not match with your username."
            },
        )

    token = guacamole.get_token(
        session.guacamole_username, session.guacamole_password
    )
    return models.GuacamoleAuthentication(
        token=json.dumps(token),
        url=config.config["extensions"]["guacamole"]["publicURI"] + "/#/",
    )


router.include_router(router=files_routes.router, prefix="/{session_id}/files")


@users_router.get(
    "/{user_id}/sessions", response_model=list[models.OwnSessionResponse]
)
def get_sessions_for_user(
    user: users_models.DatabaseUser = fastapi.Depends(
        users_injectables.get_existing_user
    ),
    current_user: users_models.DatabaseUser = fastapi.Depends(
        users_injectables.get_own_user
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
    token=fastapi.Depends(jwt_bearer.JWTBearer()),
):
    if user != current_user and not auth_injectables.RoleVerification(
        required_role=users_models.Role.ADMIN, verify=False
    )(token, db):
        raise fastapi.HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "reason": "You can only see your own sessions.",
                "technical": "If you are a project lead or administrator, please use the /sessions endpoint",
            },
        )

    return (
        []
        if not user.sessions
        else sessions.inject_attrs_in_sessions(user.sessions)
    )


def get_image_for_tool_version(db: orm.Session, version_id: int) -> str:
    version = tools_crud.get_version_by_id_or_raise(db, version_id)
    return version.tool.docker_image_template.replace("$version", version.name)


def get_readonly_image_for_version(
    version: tools_models.DatabaseVersion,
) -> str | None:
    template = version.tool.readonly_docker_image_template
    return template.replace("$version", version.name) if template else None
