# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging

import pytest

from capellacollab import config
from capellacollab.config import models as config_models
from capellacollab.sessions import crud as sessions_crud
from capellacollab.sessions import hooks as sessions_hooks
from capellacollab.sessions import models as sessions_models
from capellacollab.sessions import routes as sessions_routes
from capellacollab.sessions import util as sessions_util
from capellacollab.tools import injectables as tools_injectables
from capellacollab.tools import models as tools_models
from capellacollab.users import models as users_models


@pytest.fixture(name="mock_session_methods")
def fixture_mock_session_methods():
    pass


class MockOperator:
    environment = {}

    def start_session(self, environment, *args, **kwargs):
        self.environment = environment
        return {"port": "", "host": "", "created_at": ""}


@pytest.fixture(name="operator")
def fixture_operator():
    return MockOperator()


@pytest.fixture(name="tool")
def fixture_tool(monkeypatch: pytest.MonkeyPatch):
    tool = tools_models.DatabaseTool(
        name="test",
        integrations=tools_models.ToolIntegrations(),
        config=tools_models.ToolSessionConfiguration(
            environment={
                "TEST": "id-{CAPELLACOLLAB_SESSION_ID}",
                "TEST_DUPLICATE": "tool",
                "TEST_INVALID": "invalid_{INVALID}",
            },
            connection=tools_models.ToolSessionConnection(
                methods=[
                    tools_models.HTTPConnectionMethod(
                        environment={
                            "TEST_INNER": "inner",
                            "TEST_DUPLICATE": "overwritten",
                        }
                    )
                ]
            ),
        ),
    )

    monkeypatch.setattr(
        tools_injectables, "get_existing_tool", lambda *args, **kwargs: tool
    )
    return tool


@pytest.fixture(name="patch_irrelevant_request_session_calls")
def fixture_patch_irrelevant_request_session_calls(
    monkeypatch: pytest.MonkeyPatch,
    tool: tools_models.DatabaseTool,
):
    monkeypatch.setattr(
        tools_injectables,
        "get_existing_tool_version",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        sessions_util,
        "get_connection_method",
        lambda *args, **kwargs: tool.config.connection.methods[0],
    )
    monkeypatch.setattr(
        sessions_util,
        "raise_if_conflicting_sessions",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        sessions_util, "generate_id", lambda *args, **kwargs: "mock"
    )
    monkeypatch.setattr(
        sessions_hooks,
        "get_activated_integration_hooks",
        lambda *args, **kwargs: [],
    )
    monkeypatch.setattr(
        sessions_util, "get_docker_image", lambda *args, **kwargs: "image"
    )
    monkeypatch.setattr(
        sessions_crud, "create_session", lambda *args, **kwargs: None
    )
    monkeypatch.setattr(
        sessions_crud, "update_session_config", lambda *args, **kwargs: None
    )

    monkeypatch.setattr(
        config.config,
        "general",
        config_models.GeneralConfig(
            host="localhost", port=8080, scheme="http"
        ),
    )


@pytest.mark.usefixtures("patch_irrelevant_request_session_calls")
def test_environment_behaviour(
    monkeypatch: pytest.MonkeyPatch,
    operator: MockOperator,
    logger: logging.LoggerAdapter,
):
    """Test the behaviour of environment variables

    The rules are:

    - Environment variables for connection_method should take
    priority over the environment variables of the tool.
    - Invalid variables should be ignored and a warning should be added.
    - Variables should be resolved properly
    - Predefined variables should be available
    """

    class GetSessionsReponseMock:
        warnings = []

    response = GetSessionsReponseMock()

    monkeypatch.setattr(
        sessions_models.GetSessionsResponse,
        "model_validate",
        lambda *args: response,
    )

    sessions_routes.request_session(
        sessions_models.PostSessionRequest(
            tool_id=0,
            version_id=0,
            session_type=sessions_models.SessionType.PERSISTENT,
            connection_method_id="test",
            provisioning=[],
        ),
        users_models.DatabaseUser(name="test", role=users_models.Role.USER),
        None,
        operator,
        logger,
    )

    env = operator.environment

    # Check predefined variables
    assert env.get("CAPELLACOLLAB_SESSION_TOKEN")
    assert env.get("CAPELLACOLLAB_SESSION_ID") == "mock"
    assert env.get("CAPELLACOLLAB_SESSION_CONNECTION_METHOD_TYPE") == "http"
    assert env.get("CAPELLACOLLAB_SESSION_REQUESTER_USERNAME") == "test"
    assert env.get("CAPELLACOLLAB_SESSION_CONTAINER_PORT") == "8080"
    assert env.get("CAPELLACOLLAB_SESSIONS_SCHEME") == "http"
    assert env.get("CAPELLACOLLAB_SESSIONS_HOST") == "localhost"
    assert env.get("CAPELLACOLLAB_SESSIONS_PORT") == "8080"
    assert env.get("CAPELLACOLLAB_SESSIONS_BASE_PATH") == "/session/mock"
    assert env.get("CAPELLACOLLAB_ORIGIN_BASE_URL") == "http://localhost:8080"

    assert env["TEST"] == "id-mock"
    assert env["TEST_DUPLICATE"] == "overwritten"
    assert env["TEST_INNER"] == "inner"

    assert not env.get("TEST_INVALID")
    assert (
        response.warnings[0].err_code
        == "ENVIRONMENT_VARIABLE_RESOLUTION_FAILED"
    )


def test_environment_resolution_before_stage(logger: logging.LoggerAdapter):

    environment = {"TEST": [{"test": "test2"}]}
    rules = {
        "TEST2": tools_models.ToolSessionEnvironment(
            stage=tools_models.ToolSessionEnvironmentStage.BEFORE,
            value="{TEST[0][test]}",
        )
    }

    resolved, warnings = sessions_util.resolve_environment_variables(
        logger,
        environment,
        rules,
        stage=tools_models.ToolSessionEnvironmentStage.BEFORE,
    )

    assert not warnings
    assert resolved["TEST2"] == "test2"


def test_environment_resolution_wrong_stage(logger: logging.LoggerAdapter):

    environment = {"TEST": [{"test": "test2"}]}
    rules = {
        "TEST2": tools_models.ToolSessionEnvironment(
            stage=tools_models.ToolSessionEnvironmentStage.BEFORE,
            value="{TEST[0][test]}",
        )
    }

    resolved, warnings = sessions_util.resolve_environment_variables(
        logger,
        environment,
        rules,
        stage=tools_models.ToolSessionEnvironmentStage.AFTER,
    )

    assert not warnings
    assert "TEST2" not in resolved
