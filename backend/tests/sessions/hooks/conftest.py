# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import logging

import pytest
from sqlalchemy import orm

from capellacollab.permissions import injectables as permissions_injectables
from capellacollab.sessions import models as sessions_models
from capellacollab.sessions.hooks import interface as hooks_interface
from capellacollab.sessions.operators import k8s as k8s_operator
from capellacollab.tools import models as tools_models
from capellacollab.users import models as users_models


@pytest.fixture(name="configuration_hook_request")
def fixture_configuration_hook_request(
    db: orm.Session,
    user: users_models.DatabaseUser,
    capella_tool: tools_models.DatabaseTool,
    capella_tool_version: tools_models.DatabaseVersion,
    logger: logging.LoggerAdapter,
) -> hooks_interface.ConfigurationHookRequest:
    return hooks_interface.ConfigurationHookRequest(
        db=db,
        operator=k8s_operator.KubernetesOperator(),
        user=user,
        tool=capella_tool,
        tool_version=capella_tool_version,
        session_type=sessions_models.SessionType.PERSISTENT,
        connection_method=tools_models.GuacamoleConnectionMethod(),
        provisioning=[],
        session_id="nxylxqbmfqwvswlqlcbsirvrt",
        project_scope=None,
        pat=None,
        global_scope=permissions_injectables.get_scope(user, None),
        logger=logger,
    )


@pytest.fixture(name="post_session_creation_hook_request")
def fixture_post_session_creation_hook_request(
    db: orm.Session,
    session: sessions_models.DatabaseSession,
    user: users_models.DatabaseUser,
) -> hooks_interface.PostSessionCreationHookRequest:
    return hooks_interface.PostSessionCreationHookRequest(
        session_id="test",
        db_session=session,
        session={
            "id": "test",
            "port": 8080,
            "created_at": datetime.datetime.fromisoformat(
                "2021-01-01T00:00:00"
            ),
            "host": "test",
        },
        user=user,
        connection_method=tools_models.GuacamoleConnectionMethod(),
        operator=k8s_operator.KubernetesOperator(),
        db=db,
    )


@pytest.fixture(name="session_connection_hook_request")
def fixture_session_connection_hook_request(
    db: orm.Session,
    user: users_models.DatabaseUser,
    session: sessions_models.DatabaseSession,
    logger: logging.LoggerAdapter,
) -> hooks_interface.SessionConnectionHookRequest:
    return hooks_interface.SessionConnectionHookRequest(
        db=db,
        db_session=session,
        connection_method=tools_models.GuacamoleConnectionMethod(),
        logger=logger,
        user=user,
    )


@pytest.fixture(name="pre_session_termination_hook_request")
def fixture_pre_session_termination_hook_request(
    db: orm.Session,
    user: users_models.DatabaseUser,
    session: sessions_models.DatabaseSession,
    logger: logging.LoggerAdapter,
) -> hooks_interface.PreSessionTerminationHookRequest:
    return hooks_interface.PreSessionTerminationHookRequest(
        db=db,
        connection_method=tools_models.GuacamoleConnectionMethod(),
        operator=k8s_operator.KubernetesOperator(),
        session=session,
        global_scope=permissions_injectables.get_scope(user, None),
        logger=logger,
    )
