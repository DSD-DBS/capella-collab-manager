# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import hmac
import logging
import typing as t

import fastapi
from fastapi import status
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core import logging as log
from capellacollab.core import models as core_models
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.sessions import hooks
from capellacollab.sessions.files import routes as files_routes
from capellacollab.tools import injectables as tools_injectables
from capellacollab.tools import models as tools_models
from capellacollab.users import injectables as users_injectables
from capellacollab.users import models as users_models

from . import crud, injectables, models, operators, util
from .operators import k8s
from .operators import models as operators_models

router = fastapi.APIRouter(
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.USER
            )
        )
    ]
)

router_without_authentication = fastapi.APIRouter()

users_router = fastapi.APIRouter(
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.USER
            )
        )
    ]
)


@router.post("", response_model=models.GetSessionsResponse)
def request_session(
    body: models.PostSessionRequest,
    user: users_models.DatabaseUser = fastapi.Depends(
        users_injectables.get_own_user
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
    operator: k8s.KubernetesOperator = fastapi.Depends(operators.get_operator),
    logger: logging.LoggerAdapter = fastapi.Depends(log.get_request_logger),
):
    logger.info(
        "Starting %s session for user %s", body.session_type, user.name
    )

    # Provisioning will be supported in the future:
    # https://github.com/DSD-DBS/capella-collab-manager/issues/1004
    if (
        body.session_type == models.SessionType.PERSISTENT
        and body.provisioning
    ):
        raise fastapi.HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "reason": "Provisioning is not supported for persistent sessions.",
            },
        )

    tool = tools_injectables.get_existing_tool(body.tool_id, db)
    version = tools_injectables.get_existing_tool_version(
        tool.id, body.version_id, db
    )

    connection_method: tools_models.ToolSessionConnectionMethod = (
        util.get_connection_method(tool, body.connection_method_id)
    )

    session_id = util.generate_id()

    util.raise_if_conflicting_sessions(tool, version, body.session_type, user)

    environment = t.cast(
        dict[str, str],
        util.get_environment(user, connection_method, session_id),
    )
    volumes: list[operators_models.Volume] = []
    warnings: list[core_models.Message] = []

    for hook in hooks.get_activated_integration_hooks(tool):
        hook_result = hook.configuration_hook(
            db=db,
            user=user,
            tool_version=version,
            tool=tool,
            username=user.name,
            operator=operator,
            session_type=body.session_type,
            connection_method=connection_method,
            provisioning=body.provisioning,
        )
        environment |= hook_result.get("environment", {})
        volumes += hook_result.get("volumes", [])
        warnings += hook_result.get("warnings", [])

    local_env, local_warnings = util.resolve_environment_variables(
        logger,
        environment,
        tool.config.environment | connection_method.environment,
    )
    warnings += local_warnings
    environment |= local_env

    docker_image = util.get_docker_image(version, body.session_type)

    session = operator.start_session(
        session_id=session_id,
        image=docker_image,
        username=user.name,
        session_type=models.SessionType.PERSISTENT,
        tool=tool,
        version=version,
        environment=environment,
        ports=connection_method.ports.model_dump(),
        volumes=volumes,
        prometheus_path=tool.config.monitoring.prometheus.path,
        prometheus_port=connection_method.ports.metrics,
    )

    db_session = crud.create_session(
        db,
        models.DatabaseSession(
            id=session_id,
            tool=tool,
            version=version,
            owner=user,
            type=body.session_type,
            environment=environment,
            config={
                "port": str(session["port"]),
                "host": str(session["host"]),
            },
            created_at=session["created_at"],
            connection_method_id=connection_method.id,
        ),
    )

    hook_config: dict[str, str] = {}
    for hook in hooks.get_activated_integration_hooks(tool):
        result = hook.post_session_creation_hook(
            session_id=session_id,
            operator=operator,
            user=user,
            session=session,
            db_session=db_session,
            connection_method=connection_method,
        )

        hook_config |= result.get("config", {})

    crud.update_session_config(db, db_session, hook_config)

    response = models.GetSessionsResponse.model_validate(db_session)
    response.warnings += warnings

    return response


@router.get(
    "",
    response_model=list[models.GetSessionsResponse],
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.ADMIN
            )
        )
    ],
)
def get_all_sessions(
    db: orm.Session = fastapi.Depends(database.get_db),
):
    return crud.get_sessions(db)


@router.get(
    "/{session_id}/connection",
    response_model=core_models.PayloadResponseModel[
        models.SessionConnectionInformation
    ],
)
def get_session_connection_information(
    db: orm.Session = fastapi.Depends(database.get_db),
    session: models.DatabaseSession = fastapi.Depends(
        injectables.get_existing_session
    ),
    user: users_models.DatabaseUser = fastapi.Depends(
        users_injectables.get_own_user
    ),
    logger: logging.LoggerAdapter = fastapi.Depends(log.get_request_logger),
):
    if session.owner != user:
        raise fastapi.HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "reason": "The owner of the session does not match with your username."
            },
        )

    connection_method = util.get_connection_method(
        session.tool, session.connection_method_id
    )

    warnings: list[core_models.Message] = []
    local_storage: dict[str, str] = {}
    cookies: dict[str, str] = {}
    redirect_url = None
    t4c_token = None

    for hook in hooks.get_activated_integration_hooks(session.tool):
        hook_result = hook.session_connection_hook(
            db=db,
            user=user,
            db_session=session,
            connection_method=connection_method,
            logger=logger,
        )

        local_storage |= hook_result.get("local_storage", {})
        cookies |= hook_result.get("cookies", {})
        if hook_result.get("redirect_url"):
            redirect_url = hook_result["redirect_url"]
        if hook_result.get("t4c_token"):
            t4c_token = hook_result["t4c_token"]
        warnings += hook_result.get("warnings", [])

    return core_models.PayloadResponseModel(
        payload=models.SessionConnectionInformation(
            local_storage=local_storage,
            cookies=cookies,
            redirect_url=redirect_url,
            t4c_token=t4c_token,
        ),
        warnings=warnings,
    )


@router_without_authentication.post(
    "/{session_id}/tokens/validate",
)
def validate_session_token(
    session_id: str,
    ccm_session_token: t.Annotated[str, fastapi.Cookie()],
    db: orm.Session = fastapi.Depends(database.get_db),
):
    """Validate that the passed session token is valid for the given session."""
    session = crud.get_session_by_id(db, session_id)

    if session is None:
        return fastapi.Response(status_code=status.HTTP_401_UNAUTHORIZED)

    if hmac.compare_digest(
        ccm_session_token,
        session.environment["CAPELLACOLLAB_SESSION_TOKEN"],
    ):
        return fastapi.Response(status_code=status.HTTP_204_NO_CONTENT)

    return fastapi.Response(status_code=status.HTTP_403_FORBIDDEN)


@router.delete("/{session_id}", status_code=204)
def end_session(
    db: orm.Session = fastapi.Depends(database.get_db),
    session: models.DatabaseSession = fastapi.Depends(
        injectables.get_existing_session
    ),
    operator: k8s.KubernetesOperator = fastapi.Depends(operators.get_operator),
):
    util.terminate_session(db, session, operator)


router.include_router(router=files_routes.router, prefix="/{session_id}/files")


@users_router.get(
    "/{user_id}/sessions",
    response_model=list[models.GetSessionsResponse],
)
def get_sessions_for_user(
    user: users_models.DatabaseUser = fastapi.Depends(
        users_injectables.get_existing_user
    ),
    current_user: users_models.DatabaseUser = fastapi.Depends(
        users_injectables.get_own_user
    ),
):
    if (
        user != current_user
        and not current_user.role != users_models.Role.ADMIN
    ):
        raise fastapi.HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "reason": "You can only see your own sessions.",
                "technical": "If you are a project lead or administrator, please use the /sessions endpoint",
            },
        )

    return [
        models.GetSessionsResponse.model_validate(session)
        for session in user.sessions
    ]
