# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import abc
import dataclasses
import logging
import typing as t

from sqlalchemy import orm

from capellacollab.core import models as core_models
from capellacollab.permissions import models as permissions_models
from capellacollab.projects import models as projects_models
from capellacollab.sessions import operators
from capellacollab.sessions.operators import k8s
from capellacollab.sessions.operators import models as operators_models
from capellacollab.tools import models as tools_models
from capellacollab.users import models as users_models
from capellacollab.users.tokens import models as tokens_models

from .. import models as sessions_models


@dataclasses.dataclass()
class ConfigurationHookRequest:
    """Request type of the configuration hook

    Attributes
    ----------
    db : sqlalchemy.orm.Session
        Database session. Can be used to access the database
    operator : operators.KubernetesOperator
        Operator, which is used to spawn the session
    user : users_models.DatabaseUser
        User who has requested the session
    tool : tools_models.DatabaseTool
        Tool of the requested session
    tool_version : tools_models.DatabaseVersion
        Tool version of the requested session
    session_type : sessions_models.SessionType
        Type of the session (persistent, read-only, etc.)
    connection_method : tools_models.ToolSessionConnectionMethod
        Requested connection method for the session
    provisioning : list[sessions_models.SessionProvisioningRequest]
        List of workspace provisioning requests
    session_id: str
        ID of the session to be created
    pat: tokens_models.DatabaseUserToken | None
        Personal access token if used for authentication
    global_scope: permissions_models.GlobalScopes
        Global permission scope of the user
    logger: logging.LoggerAdapter
        Logger for the specific request
    """

    db: orm.Session
    operator: operators.KubernetesOperator
    user: users_models.DatabaseUser
    tool: tools_models.DatabaseTool
    tool_version: tools_models.DatabaseVersion
    session_type: sessions_models.SessionType
    connection_method: tools_models.ToolSessionConnectionMethod
    provisioning: list[sessions_models.SessionProvisioningRequest]
    project_scope: projects_models.DatabaseProject | None
    session_id: str
    pat: tokens_models.DatabaseUserToken | None
    global_scope: permissions_models.GlobalScopes
    logger: logging.LoggerAdapter


class ConfigurationHookResult(t.TypedDict):
    """Return type of the configuration hook

    Attributes
    ----------
    environment : dict[str, str]
        Environment variables to be injected into the session.
    volumes : list[operators_models.Volume]
        List of volumes to be mounted into the session.
    warnings : list[core_models.Message]
        List of warnings to be displayed to the user.
    init_volumes : list[operators_models.Volume]
        List of volumes to be mounted into the session preparation container.
    init_environment : dict[str, str]
        Dictionary of environment variables to be injected into the
        session preparation container.
    """

    environment: t.NotRequired[t.Mapping]
    volumes: t.NotRequired[list[operators_models.Volume]]
    warnings: t.NotRequired[list[core_models.Message]]
    init_volumes: t.NotRequired[list[operators_models.Volume]]
    init_environment: t.NotRequired[t.Mapping]
    config: t.NotRequired[t.Mapping]


@dataclasses.dataclass()
class PostSessionCreationHookRequest:
    """Request type of the post session creation hook

    Attributes
    ----------
    session_id : str
        ID of the session
    session : k8s.Session
        Session object (contains connection information)
    db_session : sessions_models.DatabaseSession
        Collaboration Manager session in the database
    operator : operators.KubernetesOperator
        Operator, which is used to spawn the session
    user : users_models.DatabaseUser
        User who has requested the session
    connection_method : tools_models.ToolSessionConnectionMethod
        Requested connection method for the session
    db : orm.Session
        Database session. Can be used to access the database
    """

    session_id: str
    session: k8s.Session
    db_session: sessions_models.DatabaseSession
    operator: operators.KubernetesOperator
    user: users_models.DatabaseUser
    connection_method: tools_models.ToolSessionConnectionMethod
    db: orm.Session


class PostSessionCreationHookResult(t.TypedDict):
    """Return type of the post session creation hook

    Attributes
    ----------
    config: dict[str, str]
        Dictionary of key-value pairs to be stored internally in the database.
        The value will not be exposed via the API.
    """

    config: t.NotRequired[t.Mapping]


@dataclasses.dataclass()
class SessionConnectionHookRequest:
    """Request type of the session connection hook

    Attributes
    ----------
    db : sqlalchemy.orm.Session
        Database session. Can be used to access the database
    db_session : sessions_models.DatabaseSession
        Collaboration Manager session in the database
    connection_method : tools_models.ToolSessionConnectionMethod
        Connection method of the session
    logger : logging.LoggerAdapter
        Logger for the specific request
    user : users_models.DatabaseUser
        User who is connecting to the session
    """

    db: orm.Session
    db_session: sessions_models.DatabaseSession
    connection_method: tools_models.ToolSessionConnectionMethod
    logger: logging.LoggerAdapter
    user: users_models.DatabaseUser


class SessionConnectionHookResult(t.TypedDict):
    """Return type of the session connection hook

    Attributes
    ----------
    local_storage :
        Dictionary of key-value pairs to be stored in the local storage
        of the frontend.
    cookies:
        Dictionary of key-value pairs to be stored as cookies in the frontend.
    redirect_url : str
        URL to redirect the user to after the session was created.
    t4c_token : str
        T4C session token to be used for T4C authentication.
    warnings : list[core_models.Message]
        List of warnings that are returned in the response payload.
    """

    local_storage: t.NotRequired[dict[str, str]]
    cookies: t.NotRequired[dict[str, str]]
    redirect_url: t.NotRequired[str]
    t4c_token: t.NotRequired[str | None]
    warnings: t.NotRequired[list[core_models.Message]]


@dataclasses.dataclass()
class PreSessionTerminationHookRequest:
    """Request type of the pre session termination hook

    Attributes
    ----------
    db : sqlalchemy.orm.Session
        Database session. Can be used to access the database
    operator : operators.KubernetesOperator
        Operator, which is used to spawn the session
    session : sessions_models.DatabaseSession
        Session which is to be terminated
    connection_method : tools_models.ToolSessionConnectionMethod
        Connection method of the session
    global_scope: permissions_models.GlobalScopes
        Global permission scope of the user
    logger: logging.LoggerAdapter
        Logger for the specific request
    """

    db: orm.Session
    operator: operators.KubernetesOperator
    session: sessions_models.DatabaseSession
    connection_method: tools_models.ToolSessionConnectionMethod
    global_scope: permissions_models.GlobalScopes
    logger: logging.LoggerAdapter


class PreSessionTerminationHookResult(t.TypedDict):
    """Return type of the pre session termination hook"""


class HookRegistration(metaclass=abc.ABCMeta):  # noqa: B024
    """Interface for session hooks

    Notes
    -----
    Session hooks have to registered in `capellacollab.sessions.hooks.__init__`

    When implementing a specific hook, do not expect positional arguments.
    The hooks are called with keyword arguments only.
    Therefore, unused arguments can be safely ignored via kwargs.

    Unnecessary hooks don't have to implemented and are skipped automatically.
    That's why the hooks in this interface are not abstract methods.
    """

    def configuration_hook(
        self,
        request: ConfigurationHookRequest,  # noqa: ARG002
    ) -> ConfigurationHookResult:
        """Hook to determine session configuration

        This hook is executed before the creation of persistent sessions.
        """

        return ConfigurationHookResult()

    async def async_configuration_hook(
        self,
        request: ConfigurationHookRequest,  # noqa: ARG002
    ) -> ConfigurationHookResult:
        """Hook to determine session configuration

        Same as configuration_hook, but async.
        """

        return ConfigurationHookResult()

    def post_session_creation_hook(
        self,
        request: PostSessionCreationHookRequest,  # noqa: ARG002
    ) -> PostSessionCreationHookResult:
        """Hook executed after session creation

        This hook is executed after a persistent session was created
        by the operator.
        """

        return PostSessionCreationHookResult()

    def session_connection_hook(
        self,
        request: SessionConnectionHookRequest,  # noqa: ARG002
    ) -> SessionConnectionHookResult:
        """Hook executed while connecting to a session

        The hook is executed each time the
        GET `/sessions/{session_id}/connection` endpoint is called.
        """

        return SessionConnectionHookResult()

    def pre_session_termination_hook(
        self,
        request: PreSessionTerminationHookRequest,  # noqa: ARG002
    ) -> PreSessionTerminationHookResult:
        """Hook executed directly before session termination

        This hook is executed before a read-only or persistent session
        is terminated by the operator.
        """
        return PreSessionTerminationHookResult()
