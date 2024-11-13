# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import json
import logging
import random
import string
import typing as t

from sqlalchemy import orm

from capellacollab.config import config
from capellacollab.core import credentials
from capellacollab.core import models as core_models
from capellacollab.sessions import hooks
from capellacollab.sessions.hooks import interface as hooks_interface
from capellacollab.sessions.operators import k8s
from capellacollab.tools import models as tools_models
from capellacollab.users import models as users_models

from . import crud, exceptions, hooks, models
from .operators import k8s

log = logging.getLogger(__name__)


def terminate_session(
    db: orm.Session,
    session: models.DatabaseSession,
    operator: k8s.KubernetesOperator,
):
    connection_method = get_connection_method(
        session.tool, session.connection_method_id
    )
    for hook in hooks.get_activated_integration_hooks(session.tool):
        hook.pre_session_termination_hook(
            hooks_interface.PreSessionTerminationHookRequest(
                db=db,
                session=session,
                operator=operator,
                connection_method=connection_method,
            )
        )

    crud.delete_session(db, session)
    operator.kill_session(session.id)


def generate_id() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=25))


def get_environment(
    user: users_models.DatabaseUser,
    connection_method: tools_models.ToolSessionConnectionMethod,
    session_id: str,
) -> models.SessionEnvironment:
    if isinstance(connection_method, tools_models.HTTPConnectionMethod):
        container_port = connection_method.ports.http
    elif isinstance(connection_method, tools_models.GuacamoleConnectionMethod):
        container_port = connection_method.ports.rdp
    else:
        container_port = -1

    return {
        "CAPELLACOLLAB_SESSION_TOKEN": credentials.generate_password(
            length=64
        ),
        "CAPELLACOLLAB_SESSION_ID": session_id,
        "CAPELLACOLLAB_SESSION_REQUESTER_USERNAME": user.name,
        "CAPELLACOLLAB_SESSIONS_BASE_PATH": f"/session/{session_id}",
        "CAPELLACOLLAB_SESSION_CONNECTION_METHOD_TYPE": connection_method.type,
        "CAPELLACOLLAB_ORIGIN_BASE_URL": f"{config.general.scheme}://{config.general.host}:{config.general.port}",
        "CAPELLACOLLAB_SESSIONS_SCHEME": config.general.scheme,
        "CAPELLACOLLAB_SESSIONS_HOST": config.general.host,
        "CAPELLACOLLAB_SESSIONS_PORT": str(config.general.port),
        "CAPELLACOLLAB_SESSION_CONTAINER_PORT": str(container_port),
    }


def raise_if_conflicting_sessions(
    tool: tools_models.DatabaseTool,
    version: tools_models.DatabaseVersion,
    workspace_type: models.SessionType,
    user: users_models.DatabaseUser,
) -> None:
    existing_tool_version_workspace_combinations = {
        (session.tool.id, session.version.id, session.type)
        for session in user.sessions
    }

    if (
        tool.id,
        version.id,
        workspace_type,
    ) in existing_tool_version_workspace_combinations:
        raise exceptions.ConflictingSessionError(tool.name, version.name)


def resolve_environment_variables(
    logger: logging.LoggerAdapter,
    environment: dict[str, t.Any],
    rules: t.Mapping[str, str | tools_models.ToolSessionEnvironment],
    stage: tools_models.ToolSessionEnvironmentStage = tools_models.ToolSessionEnvironmentStage.AFTER,
) -> tuple[dict[str, str], list[core_models.Message]]:
    resolved = {}
    warnings = []

    for key, value in rules.items():
        if isinstance(value, tools_models.ToolSessionEnvironment):
            env_value = value.value
            if value.stage != stage:
                continue
        else:
            env_value = value

        try:
            resolved[key] = env_value.format(**environment)
        except Exception:
            logger.warning(
                "Failed to resolve environment variable '%s'",
                key,
                exc_info=True,
            )
            warnings += [
                core_models.Message(
                    err_code="ENVIRONMENT_VARIABLE_RESOLUTION_FAILED",
                    title="Couldn't resolve environment variable",
                    reason=(
                        f"Failed to resolve environment variable '{key}'. "
                        "This might be due to a incorrect configuration. "
                        "Please contact your administrator. "
                        "The variable is ignored and an attempt is still made to start the session. "
                    ),
                )
            ]

    return resolved, warnings


def stringify_environment_variables(
    logger: logging.LoggerAdapter,
    environment: dict[str, t.Any],
) -> list[core_models.Message]:
    """Try to stringify non-string environment variables in the JSON format"""
    warnings = []

    for key, value in environment.copy().items():
        try:
            if not isinstance(value, str):
                environment[key] = json.dumps(value)
        except Exception:
            logger.warning(
                "Couldn't stringify environment variable '%s'",
                key,
                exc_info=True,
            )
            del environment[key]
            warnings += [
                core_models.Message(
                    title="Couldn't stringify environment variable.",
                    err_code="ENVIRONMENT_DUMPING_FAILED",
                    reason=(
                        f"Failed to resolve environment variable '{key}'. "
                        "This might be due to a incorrect configuration. "
                        "Please contact your administrator. "
                        "The variable is ignored and an attempt is still made to start the session. "
                    ),
                )
            ]

    return warnings


def get_docker_image(
    version: tools_models.DatabaseVersion,
    workspace_type: models.SessionType,
    beta: bool,
) -> str:
    """Get the Docker image for a given tool version and workspace type"""
    images = version.config.sessions.persistent.image
    template = images.beta if beta and images.beta else images.regular

    if not template:
        raise exceptions.UnsupportedSessionTypeError(
            version.tool.name, workspace_type
        )
    return template.format(version=version.name)


def get_connection_method(
    tool: tools_models.DatabaseTool, connection_method_id: str
) -> tools_models.ToolSessionConnectionMethod:
    try:
        return next(
            connection_method
            for connection_method in tool.config.connection.methods
            if connection_method.id == connection_method_id
        )
    except StopIteration:
        raise exceptions.InvalidConnectionMethodIdentifierError(
            tool.name, connection_method_id
        )


def is_session_shared_with_user(
    session: models.DatabaseSession, user: users_models.DatabaseUser
) -> bool:
    return user in [shared.user for shared in session.shared_with]
