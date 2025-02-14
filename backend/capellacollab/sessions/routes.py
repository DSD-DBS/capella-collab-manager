# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import datetime
import logging
import typing as t

import fastapi
import jwt
from fastapi import status
from sqlalchemy import orm

from capellacollab.core import database, responses
from capellacollab.core import logging as log
from capellacollab.core import models as core_models
from capellacollab.core.authentication import exceptions as auth_exceptions
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.permissions import injectables as permissions_injectables
from capellacollab.permissions import models as permissions_models
from capellacollab.projects import injectables as projects_injectables
from capellacollab.projects.permissions import (
    injectables as projects_permissions_injectables,
)
from capellacollab.projects.permissions import (
    models as projects_permissions_models,
)
from capellacollab.sessions import hooks as sessions_hooks
from capellacollab.sessions.files import routes as files_routes
from capellacollab.sessions.hooks import interface as hooks_interface
from capellacollab.tools import exceptions as tools_exceptions
from capellacollab.tools import injectables as tools_injectables
from capellacollab.tools import models as tools_models
from capellacollab.tools import util as tools_util
from capellacollab.users import crud as users_crud
from capellacollab.users import exceptions as users_exceptions
from capellacollab.users import injectables as users_injectables
from capellacollab.users import models as users_models
from capellacollab.users.tokens import models as tokens_models

from . import auth, crud, exceptions, injectables, models, operators, util
from .operators import k8s
from .operators import models as operators_models

router = fastapi.APIRouter()

users_router = fastapi.APIRouter()


@router.post(
    "",
    response_model=models.Session,
    responses=responses.translate_exceptions_to_openapi_schema(
        [
            exceptions.UnsupportedSessionTypeError,
            exceptions.ConflictingSessionError,
            exceptions.ToolAndModelMismatchError,
            exceptions.InvalidConnectionMethodIdentifierError,
            exceptions.WorkspaceMountingNotAllowedError,
            exceptions.TooManyModelsRequestedToProvisionError,
            exceptions.ProvisioningUnsupportedError,
            tools_exceptions.ToolNotFoundError,
            tools_exceptions.ToolVersionNotFoundError,
        ],
    ),
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    user=permissions_models.UserScopes(
                        sessions={permissions_models.UserTokenVerb.CREATE}
                    )
                )
            ),
        )
    ],
)
async def request_session(
    body: models.PostSessionRequest,
    user: t.Annotated[users_models.DatabaseUser, fastapi.Depends(
        users_injectables.get_own_user
    )],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
    operator: t.Annotated[k8s.KubernetesOperator, fastapi.Depends(operators.get_operator)],
    logger: t.Annotated[logging.LoggerAdapter, fastapi.Depends(log.get_request_logger)],
    authentication_information: t.Annotated[tuple[
        users_models.DatabaseUser, tokens_models.DatabaseUserToken | None
    ], fastapi.Depends(
        auth_injectables.AuthenticationInformationValidation()
    )],
    global_scope: t.Annotated[permissions_models.GlobalScopes, fastapi.Depends(
        permissions_injectables.get_scope
    )],
):
    """Request a session.

    If requested with a project slug (required for read-only sessions),
    the requesting user must have the permissions `provisioning:get` in the project.
    """
    logger.info(
        "Starting %s session for user %s", body.session_type, user.name
    )

    tool = tools_injectables.get_existing_tool(body.tool_id, db)
    version = tools_injectables.get_existing_tool_version(
        tool.id, body.version_id, db
    )

    if body.connection_method_id:
        connection_method: tools_models.ToolSessionConnectionMethod = (
            util.get_connection_method(tool, body.connection_method_id)
        )
    else:
        connection_method = tool.config.connection.methods[0]

    session_id = util.generate_id()

    util.raise_if_conflicting_sessions(tool, version, body.session_type, user)

    project_scope = None
    if body.project_slug:
        project_scope = projects_injectables.get_existing_project(
            body.project_slug, db
        )

        projects_permissions_injectables.ProjectPermissionValidation(
            required_scope=projects_permissions_models.ProjectUserScopes(
                provisioning={permissions_models.UserTokenVerb.GET}
            )
        )(
            projects_permissions_injectables.get_scope(
                authentication_information, global_scope, project_scope, db
            ),
            project_scope,
        )

    environment = t.cast(
        dict[str, str],
        util.get_environment(user, connection_method, session_id),
    )
    volumes: list[operators_models.Volume] = []
    warnings: list[core_models.Message] = []
    init_volumes: list[operators_models.Volume] = []
    init_environment: dict[str, str] = {}
    hook_config: dict[str, str] = {}

    hook_request = hooks_interface.ConfigurationHookRequest(
        db=db,
        user=user,
        tool_version=version,
        tool=tool,
        operator=operator,
        session_type=body.session_type,
        connection_method=connection_method,
        provisioning=body.provisioning,
        session_id=session_id,
        project_scope=project_scope,
        pat=authentication_information[1],
        global_scope=global_scope,
    )

    for hook_result in await util.schedule_configuration_hooks(
        hook_request, tool
    ):
        environment |= hook_result.get("environment", {})
        init_environment |= hook_result.get("init_environment", {})
        volumes += hook_result.get("volumes", [])
        init_volumes += hook_result.get("init_volumes", [])
        warnings += hook_result.get("warnings", [])
        hook_config |= hook_result.get("config", {})

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

    docker_image = util.get_docker_image(
        version, body.session_type, user.beta_tester
    )

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
        "capellacollab/workload": "session",
        "capellacollab/session-id": session_id,
        "capellacollab/owner-id": str(user.id),
    }

    session = operator.start_session(
        session_id=session_id,
        image=docker_image,
        username=user.name,
        session_type=body.session_type,
        tool=tool,
        environment=environment,
        init_environment=init_environment,
        ports=tools_util.resolve_tool_ports(connection_method.ports),
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
            project=project_scope,
        ),
    )

    for hook in sessions_hooks.get_activated_integration_hooks(tool):
        result = hook.post_session_creation_hook(
            hooks_interface.PostSessionCreationHookRequest(
                session_id=session_id,
                operator=operator,
                user=user,
                session=session,
                db_session=db_session,
                connection_method=connection_method,
                db=db,
            )
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
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        sessions={permissions_models.UserTokenVerb.GET}
                    )
                )
            ),
        )
    ],
)
def get_all_sessions(
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
):
    return crud.get_sessions(db)


@router.get(
    "/{session_id}",
    response_model=models.Session,
    responses=responses.translate_exceptions_to_openapi_schema(
        [
            exceptions.SessionNotFoundError,
            exceptions.SessionNotOwnedError,
        ]
    ),
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    user=permissions_models.UserScopes(
                        sessions={permissions_models.UserTokenVerb.GET}
                    )
                )
            ),
        )
    ],
)
def get_session(
    session: t.Annotated[models.DatabaseSession, fastapi.Depends(
        injectables.get_existing_session_including_shared
    )],
):
    return session


@router.post(
    "/{session_id}/shares",
    response_model=models.SessionSharing,
    responses=responses.translate_exceptions_to_openapi_schema(
        [
            exceptions.InvalidConnectionMethodIdentifierError,
            exceptions.SessionNotFoundError,
            exceptions.SessionNotOwnedError,
            exceptions.SessionAlreadySharedError,
            exceptions.SessionSharingNotSupportedError,
            users_exceptions.UserNotFoundError,
        ],
    ),
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    user=permissions_models.UserScopes(
                        sessions={permissions_models.UserTokenVerb.UPDATE}
                    )
                )
            ),
        )
    ],
)
def share_session(
    body: models.ShareSessionRequest,
    session: t.Annotated[models.DatabaseSession, fastapi.Depends(
        injectables.get_existing_session
    )],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
):
    user_to_share_with = users_crud.get_user_by_name(db, body.username)
    if not user_to_share_with:
        raise users_exceptions.UserNotFoundError(username=body.username)
    if session.owner == user_to_share_with or util.is_session_shared_with_user(
        session, user_to_share_with
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
    responses=responses.translate_exceptions_to_openapi_schema(
        [
            exceptions.InvalidConnectionMethodIdentifierError,
            exceptions.SessionNotFoundError,
            exceptions.SessionNotOwnedError,
        ],
    ),
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    user=permissions_models.UserScopes(
                        sessions={permissions_models.UserTokenVerb.GET}
                    )
                )
            ),
        )
    ],
)
def get_session_connection_information(
    response: fastapi.Response,
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
    session: t.Annotated[models.DatabaseSession, fastapi.Depends(
        injectables.get_existing_session_including_shared
    )],
    user: t.Annotated[users_models.DatabaseUser, fastapi.Depends(
        users_injectables.get_own_user
    )],
    logger: t.Annotated[logging.LoggerAdapter, fastapi.Depends(log.get_request_logger)],
):
    connection_method = util.get_connection_method(
        session.tool, session.connection_method_id
    )

    warnings: list[core_models.Message] = []
    local_storage: dict[str, str] = {}
    cookies: dict[str, str] = {}
    redirect_url = None
    t4c_token = None

    for hook in sessions_hooks.get_activated_integration_hooks(session.tool):
        hook_result = hook.session_connection_hook(
            hooks_interface.SessionConnectionHookRequest(
                db=db,
                db_session=session,
                connection_method=connection_method,
                logger=logger,
                user=user,
            )
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


@router.post(
    "/{session_id}/tokens/validate",
)
def validate_session_token(
    session_id: str,
    ccm_session_token: t.Annotated[str | None, fastapi.Cookie()] = None,
):
    """Validate that the passed session token is valid for the given session."""
    if not ccm_session_token:
        return fastapi.Response(status_code=status.HTTP_401_UNAUTHORIZED)

    assert auth.PUBLIC_KEY

    try:
        decoded_token = jwt.decode(
            jwt=ccm_session_token,
            key=auth.PUBLIC_KEY,
            algorithms=["RS256"],
            options={"require": ["exp", "iat"]},
        )
    except jwt.exceptions.ExpiredSignatureError:
        return auth_exceptions.TokenSignatureExpired()
    except jwt.exceptions.PyJWTError as e:
        raise auth_exceptions.JWTValidationFailed() from e

    if decoded_token.get("session", {}).get("id") != session_id:
        return fastapi.Response(status_code=status.HTTP_403_FORBIDDEN)

    return fastapi.Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    "/{session_id}",
    status_code=204,
    responses=responses.translate_exceptions_to_openapi_schema(
        [
            exceptions.SessionNotFoundError,
            exceptions.SessionNotOwnedError,
        ]
    ),
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    user=permissions_models.UserScopes(
                        sessions={permissions_models.UserTokenVerb.DELETE}
                    )
                )
            ),
        )
    ],
)
def terminate_session(
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
    session: t.Annotated[models.DatabaseSession, fastapi.Depends(
        injectables.get_existing_session
    )],
    operator: t.Annotated[k8s.KubernetesOperator, fastapi.Depends(operators.get_operator)],
    global_scope: t.Annotated[permissions_models.GlobalScopes, fastapi.Depends(
        permissions_injectables.get_scope
    )],
):
    util.terminate_session(db, session, operator, global_scope)


router.include_router(router=files_routes.router, prefix="/{session_id}/files")


@users_router.get(
    "/{user_id}/sessions",
    response_model=list[models.Session],
    responses=responses.translate_exceptions_to_openapi_schema(
        [
            users_exceptions.UserNotFoundError,
            exceptions.SessionNotOwnedError,
            exceptions.SessionForbiddenError,
        ],
    ),
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    user=permissions_models.UserScopes(
                        sessions={permissions_models.UserTokenVerb.GET}
                    )
                )
            ),
        )
    ],
)
def get_sessions_for_user(
    user: t.Annotated[users_models.DatabaseUser, fastapi.Depends(
        users_injectables.get_existing_user
    )],
    current_user: t.Annotated[users_models.DatabaseUser, fastapi.Depends(
        users_injectables.get_own_user
    )],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
    global_scope: t.Annotated[permissions_models.GlobalScopes, fastapi.Depends(
        permissions_injectables.get_scope
    )],
):
    """Get all sessions for a user.

    You can request your own sessions
    or the sessions of another user if you have the `admin.users:get` permission.
    """

    if user != current_user and permissions_models.UserTokenVerb.GET not in (
        global_scope.admin.users
    ):
        raise exceptions.SessionForbiddenError()

    return user.sessions + list(
        crud.get_shared_sessions_for_user(db, current_user)
    )
