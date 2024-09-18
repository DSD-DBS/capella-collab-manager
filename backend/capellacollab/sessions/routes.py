# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import datetime
import hmac
import logging
import typing as t

import fastapi
from fastapi import status
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core import logging as log
from capellacollab.core import models as core_models
from capellacollab.core import responses
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.sessions import hooks
from capellacollab.sessions.files import routes as files_routes
from capellacollab.tools import exceptions as tools_exceptions
from capellacollab.tools import injectables as tools_injectables
from capellacollab.tools import models as tools_models
from capellacollab.users import crud as users_crud
from capellacollab.users import exceptions as users_exceptions
from capellacollab.users import injectables as users_injectables
from capellacollab.users import models as users_models

from . import crud, exceptions, injectables, models, operators, util
from .operators import k8s
from .operators import models as operators_models

router = fastapi.APIRouter(
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.USER
            )
        )
    ],
    responses=responses.api_exceptions(include_authentication=True),
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


@router.post(
    "",
    response_model=models.Session,
    responses=responses.api_exceptions(
        [
            exceptions.UnsupportedSessionTypeError(
                tool_name="test", session_type=models.SessionType.PERSISTENT
            ),
            exceptions.ConflictingSessionError(
                tool_name="test", version_name="test"
            ),
            exceptions.ToolAndModelMismatchError(
                tool_name="test", version_name="test", model_name="test"
            ),
            exceptions.InvalidConnectionMethodIdentifierError(
                tool_name="test", connection_method_id="default"
            ),
            exceptions.WorkspaceMountingNotAllowedError(tool_name="test"),
            exceptions.TooManyModelsRequestedToProvisionError(
                max_number_of_models=1
            ),
            exceptions.ProvisioningUnsupportedError(),
            tools_exceptions.ToolNotFoundError(tool_id=1),
            tools_exceptions.ToolVersionNotFoundError(version_id=1),
        ],
    ),
)
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
        raise exceptions.ProvisioningUnsupportedError()

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
    init_volumes: list[operators_models.Volume] = []
    init_environment: dict[str, str] = {}

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
            session_id=session_id,
        )
        environment |= hook_result.get("environment", {})
        init_environment |= hook_result.get("init_environment", {})
        volumes += hook_result.get("volumes", [])
        init_volumes += hook_result.get("init_volumes", [])
        warnings += hook_result.get("warnings", [])

    local_env, local_warnings = util.resolve_environment_variables(
        logger,
        environment,
        tool.config.environment | connection_method.environment,
        stage=tools_models.ToolSessionEnvironmentStage.BEFORE,
    )
    warnings += local_warnings
    environment |= local_env

    warnings += util.stringify_environment_variables(logger, environment)
    warnings += util.stringify_environment_variables(logger, init_environment)

    local_env, local_warnings = util.resolve_environment_variables(
        logger,
        environment,
        tool.config.environment | connection_method.environment,
        stage=tools_models.ToolSessionEnvironmentStage.AFTER,
    )
    warnings += local_warnings
    environment |= local_env

    docker_image = util.get_docker_image(version, body.session_type)

    annotations: dict[str, str] = {
        "capellacollab/owner-name": user.name,
        "capellacollab/owner-id": str(user.id),
        "capellacollab/tool-name": tool.name,
        "capellacollab/tool-id": str(tool.id),
        "capellacollab/tool-version-name": version.name,
        "capellacollab/tool-version-id": str(version.id),
        "capellacollab/session-type": body.session_type.value,
        "capellacollab/session-id": session_id,
        "capellacollab/connection-method-id": connection_method.id,
        "capellacollab/connection-method-name": connection_method.name,
    }

    labels: dict[str, str] = {
        "capellacollab/session-id": session_id,
        "capellacollab/owner-id": str(user.id),
    }

    session = operator.start_session(
        session_id=session_id,
        image=docker_image,
        username=user.name,
        session_type=body.session_type,
        tool=tool,
        version=version,
        environment=environment,
        init_environment=init_environment,
        ports=connection_method.ports.model_dump(),
        volumes=volumes,
        init_volumes=init_volumes,
        annotations=annotations,
        labels=labels,
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

    response = models.Session.model_validate(db_session)
    response.warnings += warnings

    return response


@router.get(
    "",
    response_model=list[models.Session],
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
    "/{session_id}",
    response_model=models.Session,
    responses=responses.api_exceptions(
        [
            exceptions.SessionNotFoundError(session_id="test"),
            exceptions.SessionNotOwnedError(session_id="test"),
        ]
    ),
)
def get_session(
    session: models.DatabaseSession = fastapi.Depends(
        injectables.get_existing_session
    ),
):
    return session


@router.post(
    "/{session_id}/shares",
    response_model=models.SessionSharing,
    responses=responses.api_exceptions(
        [
            exceptions.InvalidConnectionMethodIdentifierError(
                tool_name="test", connection_method_id="default"
            ),
            exceptions.SessionNotFoundError(session_id="test"),
            exceptions.SessionNotOwnedError(session_id="test"),
            exceptions.SessionAlreadySharedError(username="test"),
            exceptions.SessionSharingNotSupportedError(
                tool_name="test", connection_method_name="test"
            ),
            users_exceptions.UserNotFoundError(username="test"),
        ],
    ),
)
def share_session(
    body: models.ShareSessionRequest,
    session: models.DatabaseSession = fastapi.Depends(
        injectables.get_existing_session
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    user_to_share_with = users_crud.get_user_by_name(db, body.username)
    if not user_to_share_with:
        raise users_exceptions.UserNotFoundError(username=body.username)
    if (
        session.owner == user_to_share_with
        or util.is_session_shared_with_user(session, user_to_share_with)
    ):
        raise exceptions.SessionAlreadySharedError(user_to_share_with.name)

    connection_method = util.get_connection_method(
        tool=session.tool, connection_method_id=session.connection_method_id
    )
    if not connection_method.sharing.enabled:
        raise exceptions.SessionSharingNotSupportedError(
            tool_name=session.tool.name,
            connection_method_name=connection_method.name,
        )

    session_share = models.DatabaseSharedSession(
        created_at=datetime.datetime.now(datetime.UTC),
        session=session,
        user=user_to_share_with,
    )

    return crud.create_shared_session(db, session_share)


@router.get(
    "/{session_id}/connection",
    response_model=core_models.PayloadResponseModel[
        models.SessionConnectionInformation
    ],
    responses=responses.api_exceptions(
        [
            exceptions.InvalidConnectionMethodIdentifierError(
                tool_name="test", connection_method_id="default"
            ),
            exceptions.SessionNotFoundError(session_id="test"),
            exceptions.SessionNotOwnedError(session_id="test"),
        ],
    ),
)
def get_session_connection_information(
    response: fastapi.Response,
    db: orm.Session = fastapi.Depends(database.get_db),
    session: models.DatabaseSession = fastapi.Depends(
        injectables.get_existing_session_including_shared
    ),
    user: users_models.DatabaseUser = fastapi.Depends(
        users_injectables.get_own_user
    ),
    logger: logging.LoggerAdapter = fastapi.Depends(log.get_request_logger),
):
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

    for c_key, c_value in cookies.items():
        responses.set_secure_cookie(
            response=response,
            key=c_key,
            value=c_value,
            path=f"/session/{session.id}",
            expires=datetime.datetime.now(datetime.UTC)
            + datetime.timedelta(hours=24),
        )

    return core_models.PayloadResponseModel(
        payload=models.SessionConnectionInformation(
            local_storage=local_storage,
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


@router.delete(
    "/{session_id}",
    status_code=204,
    responses=responses.api_exceptions(
        [
            exceptions.SessionNotFoundError(session_id="test"),
            exceptions.SessionNotOwnedError(session_id="test"),
        ]
    ),
)
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
    response_model=list[models.Session],
    responses=responses.api_exceptions(
        [
            users_exceptions.UserNotFoundError(user_id=1),
            exceptions.SessionNotOwnedError(session_id="test"),
            exceptions.SessionForbiddenError(),
        ],
        minimum_role=users_models.Role.USER,
    ),
)
def get_sessions_for_user(
    user: users_models.DatabaseUser = fastapi.Depends(
        users_injectables.get_existing_user
    ),
    current_user: users_models.DatabaseUser = fastapi.Depends(
        users_injectables.get_own_user
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    if (
        user != current_user
        and not current_user.role != users_models.Role.ADMIN
    ):
        raise exceptions.SessionForbiddenError()

    return user.sessions + list(
        crud.get_shared_sessions_for_user(db, current_user)
    )
