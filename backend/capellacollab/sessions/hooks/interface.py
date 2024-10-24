# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import abc
import logging
import typing as t

from sqlalchemy import orm

from capellacollab.core import models as core_models
from capellacollab.sessions import operators
from capellacollab.sessions.operators import k8s
from capellacollab.sessions.operators import models as operators_models
from capellacollab.tools import models as tools_models
from capellacollab.users import models as users_models

from .. import models as sessions_models


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


class PostSessionCreationHookResult(t.TypedDict):
    """Return type of the post session creation hook

    Attributes
    ----------
    config: dict[str, str]
        Dictionary of key-value pairs to be stored internally in the database.
        The value will not be exposed via the API.
    """

    config: t.NotRequired[t.Mapping]


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


class PreSessionTerminationHookResult(t.TypedDict):
    """Return type of the pre session termination hook"""


class HookRegistration(metaclass=abc.ABCMeta):
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

    # pylint: disable=unused-argument
    def configuration_hook(
        self,
        db: orm.Session,
        operator: operators.KubernetesOperator,
        user: users_models.DatabaseUser,
        tool: tools_models.DatabaseTool,
        tool_version: tools_models.DatabaseVersion,
        session_type: sessions_models.SessionType,
        connection_method: tools_models.ToolSessionConnectionMethod,
        provisioning: list[sessions_models.SessionProvisioningRequest],
        session_id: str,
        **kwargs,
    ) -> ConfigurationHookResult:
        """Hook to determine session configuration

        This hook is executed before the creation of persistent sessions.

        Parameters
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
        Returns
        -------
        result : ConfigurationHookResult
        """

        return ConfigurationHookResult()

    def post_session_creation_hook(
        self,
        session_id: str,
        session: k8s.Session,
        db_session: sessions_models.DatabaseSession,
        operator: operators.KubernetesOperator,
        user: users_models.DatabaseUser,
        connection_method: tools_models.ToolSessionConnectionMethod,
        **kwargs,
    ) -> PostSessionCreationHookResult:
        """Hook executed after session creation

        This hook is executed after a persistent session was created
        by the operator.

        Parameters
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

        Returns
        -------
        result : PostSessionCreationHookResult
        """

        return PostSessionCreationHookResult()

    # pylint: disable=unused-argument
    def session_connection_hook(
        self,
        db: orm.Session,
        db_session: sessions_models.DatabaseSession,
        connection_method: tools_models.ToolSessionConnectionMethod,
        logger: logging.LoggerAdapter,
        **kwargs,
    ) -> SessionConnectionHookResult:
        """Hook executed while connecting to a session

        The hook is executed each time the
        GET `/sessions/{session_id}/connection` endpoint is called.

        Parameters
        ----------
        db : sqlalchemy.orm.Session
            Database session. Can be used to access the database
        db_session : sessions_models.DatabaseSession
            Collaboration Manager session in the database
        connection_method : tools_models.ToolSessionConnectionMethod
            Connection method of the session
        logger : logging.LoggerAdapter
            Logger for the specific request
        Returns
        -------
        result : SessionConnectionHookResult
        """

        return SessionConnectionHookResult()

    def pre_session_termination_hook(
        self,
        db: orm.Session,
        operator: operators.KubernetesOperator,
        session: sessions_models.DatabaseSession,
        connection_method: tools_models.ToolSessionConnectionMethod,
        **kwargs,
    ) -> PreSessionTerminationHookResult:
        """Hook executed directly before session termination

        This hook is executed before a read-only or persistent session
        is terminated by the operator.

        Parameters
        ----------
        db : sqlalchemy.orm.Session
            Database session. Can be used to access the database
        operator : operators.KubernetesOperator
            Operator, which is used to spawn the session
        session : sessions_models.DatabaseSession
            Session which is to be terminated
        connection_method : tools_models.ToolSessionConnectionMethod
            Connection method of the session

        Returns
        -------
        result : PreSessionTerminationHookResult
        """
        return PreSessionTerminationHookResult()
