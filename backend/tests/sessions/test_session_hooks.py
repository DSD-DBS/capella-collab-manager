# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import logging
import typing as t

import fastapi
import pytest
from sqlalchemy import orm

from capellacollab import __main__
from capellacollab.sessions import crud as sessions_crud
from capellacollab.sessions import hooks as sessions_hooks
from capellacollab.sessions import models as sessions_models
from capellacollab.sessions import operators
from capellacollab.sessions import routes as sessions_routes
from capellacollab.sessions import util as sessions_util
from capellacollab.sessions.hooks import interface as hooks_interface
from capellacollab.sessions.operators import k8s
from capellacollab.tools import models as tools_models
from capellacollab.users import models as users_models


class MockOperator:
    # pylint: disable=unused-argument
    def start_session(self, *args, **kwargs) -> k8s.Session:
        return k8s.Session(
            id="test", port=1, created_at=datetime.datetime.now(), host="test"
        )

    def kill_session(self, *args, **kwargs) -> None:
        pass

    # pylint: disable=unused-argument
    def create_persistent_volume(self, *args, **kwargs):
        return


class TestSessionHook(hooks_interface.HookRegistration):
    configuration_hook_counter = 0
    post_session_creation_hook_counter = 0
    session_connection_hook_counter = 0
    post_termination_hook_counter = 0

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
    ) -> hooks_interface.ConfigurationHookResult:
        self.configuration_hook_counter += 1
        return hooks_interface.ConfigurationHookResult()

    def post_session_creation_hook(
        self,
        session_id: str,
        session: k8s.Session,
        db_session: sessions_models.DatabaseSession,
        operator: operators.KubernetesOperator,
        user: users_models.DatabaseUser,
        connection_method: tools_models.ToolSessionConnectionMethod,
        **kwargs,
    ) -> hooks_interface.PostSessionCreationHookResult:
        self.post_session_creation_hook_counter += 1
        return hooks_interface.PostSessionCreationHookResult()

    def session_connection_hook(
        self,
        db: orm.Session,
        db_session: sessions_models.DatabaseSession,
        connection_method: tools_models.ToolSessionConnectionMethod,
        logger: logging.LoggerAdapter,
        **kwargs,
    ) -> hooks_interface.SessionConnectionHookResult:
        self.session_connection_hook_counter += 1
        return hooks_interface.SessionConnectionHookResult()

    def pre_session_termination_hook(
        self,
        db: orm.Session,
        operator: operators.KubernetesOperator,
        session: sessions_models.DatabaseSession,
        connection_method: tools_models.ToolSessionConnectionMethod,
        **kwargs,
    ) -> hooks_interface.PreSessionTerminationHookResult:
        self.post_termination_hook_counter += 1
        return hooks_interface.PreSessionTerminationHookResult()


@pytest.fixture(autouse=True, name="session_hook")
def fixture_session_hook(monkeypatch: pytest.MonkeyPatch) -> TestSessionHook:
    hook = TestSessionHook()

    REGISTER_HOOKS_AUTO_USE: dict[str, hooks_interface.HookRegistration] = {
        "test": hook,
    }

    monkeypatch.setattr(
        sessions_hooks, "REGISTER_HOOKS_AUTO_USE", REGISTER_HOOKS_AUTO_USE
    )
    return hook


@pytest.fixture(autouse=True, name="mockoperator")
def fixture_mockoperator() -> t.Generator[MockOperator, None, None]:
    mock = MockOperator()

    def get_mock_operator():
        return mock

    __main__.app.dependency_overrides[operators.get_operator] = (
        get_mock_operator
    )
    yield mock
    del __main__.app.dependency_overrides[operators.get_operator]


@pytest.mark.usefixtures("mock_session_injection", "tool_version")
def test_hook_calls_during_session_request(
    monkeypatch: pytest.MonkeyPatch,
    db: orm.Session,
    user: users_models.DatabaseUser,
    mockoperator: MockOperator,
    session_hook: TestSessionHook,
    tool: tools_models.DatabaseTool,
):
    """Test that the relevant session hooks are called
    during a session request.

    In the request session route, the configuration hook and
    the post session creation hook are called.
    """

    monkeypatch.setattr(
        sessions_util,
        "get_docker_image",
        lambda *args, **kwargs: "placeholder",
    )

    sessions_routes.request_session(
        sessions_models.PostSessionRequest(
            tool_id=0,
            version_id=0,
            session_type=sessions_models.SessionType.PERSISTENT,
            connection_method_id=tool.config.connection.methods[0].id,
            provisioning=[],
        ),
        user,
        db,
        mockoperator,  # type: ignore
        logging.getLogger("test"),
    )

    assert session_hook.configuration_hook_counter == 1
    assert session_hook.post_session_creation_hook_counter == 1
    assert session_hook.session_connection_hook_counter == 0
    assert session_hook.post_termination_hook_counter == 0


def test_hook_call_during_session_connection(
    db: orm.Session,
    session: sessions_models.DatabaseSession,
):
    """Test that the session hook is called when connecting to a session"""

    sessions_routes.get_session_connection_information(
        fastapi.Response(),
        db,
        session,
        session.owner,
        logging.getLogger("test"),
    )


def test_hook_calls_during_session_termination(
    monkeypatch: pytest.MonkeyPatch,
    mockoperator: MockOperator,
    db: orm.Session,
    session: sessions_models.DatabaseSession,
):
    monkeypatch.setattr(
        sessions_crud,
        "delete_session",
        lambda *args, **kwargs: None,
    )

    sessions_routes.terminate_session(
        db,
        session,
        mockoperator,  # type: ignore
    )
