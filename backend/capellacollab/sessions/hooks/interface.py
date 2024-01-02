# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import abc

from sqlalchemy import orm

from capellacollab.core import models as core_models
from capellacollab.sessions import operators
from capellacollab.sessions.operators import models as operators_models
from capellacollab.tools import models as tools_models
from capellacollab.users import models as users_models

from .. import models as sessions_models


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
        tool_version: tools_models.DatabaseVersion,
        tool: tools_models.DatabaseTool,
        **kwargs,
    ) -> tuple[
        dict[str, str],
        list[operators_models.Volume],
        list[core_models.Message],
    ]:
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
        token : dict[str, t.Any]
            JWT token used for authentication of the user


        Returns
        -------
        environment : dict[str, str]
            Environment variables to be injected into the session.
        volumes : list[operators_models.Volume]
            List of volumes to be mounted into the session.
        warnings : list[core_models.Message]
            List of warnings to be displayed to the user.
        """

        return {}, [], []

    def post_session_creation_hook(
        self,
        session_id: str,
        operator: operators.KubernetesOperator,
        user: users_models.DatabaseUser,
        **kwargs,
    ):
        """Hook executed after session creation

        This hook is executed after a persistent session was created
        by the operator.

        Parameters
        ----------
        session_id : str
            ID of the session
        operator : operators.KubernetesOperator
            Operator, which is used to spawn the session
        user : users_models.DatabaseUser
            User who has requested the session
        """

    def pre_session_termination_hook(
        self,
        db: orm.Session,
        operator: operators.KubernetesOperator,
        session: sessions_models.DatabaseSession,
        **kwargs,
    ):
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
        """
