# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import abc
import typing as t

from sqlalchemy import orm

from capellacollab.core import models as core_models
from capellacollab.sessions import operators
from capellacollab.tools import models as tools_models
from capellacollab.users import models as users_models

from .. import models as sessions_models


class HookRegistration(metaclass=abc.ABCMeta):
    def configuration_hook(
        self,
        db: orm.Session,
        user: users_models.DatabaseUser,
        tool_version: tools_models.DatabaseVersion,
        tool: tools_models.DatabaseTool,
        token: dict[str, t.Any],
        **kwargs,
    ) -> tuple[dict[str, str], list[core_models.Message]]:
        """Hook to determine session configuration

        This hook is executed before session creation.

        Parameters
        ----------
        db : sqlalchemy.orm.Session
            Database session. Can be used to access the database
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
        warnings : list[core_models.Message]
            List of warnings to be displayed to the user.
        """

    def post_session_creation_hook(
        self,
        session_id: str,
        operator: operators.KubernetesOperator,
        user: users_models.DatabaseUser,
        **kwargs,
    ):
        """Hook executed after session creation

        This hook is executed after the session was created by the operator.

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

        This hook is executed after the session was terminated by the operator.

        Parameters
        ----------
        db : sqlalchemy.orm.Session
            Database session. Can be used to access the database
        operator : operators.KubernetesOperator
            Operator, which is used to spawn the session
        session : sessions_models.DatabaseSession
            Session which was terminated
        """
