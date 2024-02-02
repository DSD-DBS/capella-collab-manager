# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

import pytest
from sqlalchemy import orm

from capellacollab import __main__
from capellacollab.core import models as core_models
from capellacollab.sessions import crud as sessions_crud
from capellacollab.sessions import hooks as sessions_hooks
from capellacollab.sessions import models as sessions_models
from capellacollab.sessions import operators
from capellacollab.sessions import routes as sessions_routes
from capellacollab.sessions.hooks import interface as hooks_interface
from capellacollab.tools import injectables as tools_injectables
from capellacollab.tools import models as tools_models
from capellacollab.tools.integrations import models as tools_integration_models
from capellacollab.users import models as users_models


class MockOperator:
    def start_session(self, *args, **kwargs) -> dict[str, t.Any]:
        pass

    def kill_session(self, *args, **kwargs) -> None:
        pass

    def create_persistent_volume(self, *args, **kwargs):
        return


class TestSessionHook(hooks_interface.HookRegistration):
    configuration_hook_counter = 0
    post_creation_hook_counter = 0
    post_termination_hook_counter = 0

    def configuration_hook(
        self,
        db: orm.Session,
        user: users_models.DatabaseUser,
        tool_version: tools_models.DatabaseVersion,
        tool: tools_models.DatabaseTool,
        username: str,
        **kwargs,
    ) -> tuple[dict[str, str], list[core_models.Message]]:
        self.configuration_hook_counter += 1
        return {}, [], []

    def post_session_creation_hook(
        self,
        session_id: str,
        operator: operators.KubernetesOperator,
        user: users_models.DatabaseUser,
        **kwargs,
    ):
        self.post_creation_hook_counter += 1

    def pre_session_termination_hook(
        self,
        db: orm.Session,
        operator: operators.KubernetesOperator,
        session: sessions_models.DatabaseSession,
        **kwargs,
    ):
        self.post_termination_hook_counter += 1


@pytest.fixture(autouse=True, name="session_hook")
def fixture_session_hook(monkeypatch: pytest.MonkeyPatch) -> TestSessionHook:
    hook = TestSessionHook()

    REGISTERED_HOOKS: dict[str, hooks_interface.HookRegistration] = {
        "test": hook,
    }

    monkeypatch.setattr(sessions_hooks, "REGISTERED_HOOKS", REGISTERED_HOOKS)
    return hook


@pytest.fixture(autouse=True, name="mockoperator")
def fixture_mockoperator() -> MockOperator:
    mock = MockOperator()

    def get_mock_operator():
        return mock

    __main__.app.dependency_overrides[
        operators.get_operator
    ] = get_mock_operator
    yield mock
    del __main__.app.dependency_overrides[operators.get_operator]


@pytest.fixture(autouse=True, name="tool_with_test_integration")
def fixture_tool_with_test_integration(
    monkeypatch: pytest.MonkeyPatch,
) -> tools_models.DatabaseTool:
    mock_integration = tools_integration_models.DatabaseToolIntegrations()
    mock_integration.test = True
    tool = tools_models.DatabaseTool(
        id=0,
        name="test",
        docker_image_template="test",
        integrations=mock_integration,
    )

    def mock_get_existing_tool(*args, **kwargs) -> tools_models.DatabaseTool:
        return tool

    monkeypatch.setattr(
        tools_injectables, "get_existing_tool", mock_get_existing_tool
    )
    return tool


@pytest.fixture(autouse=True, name="tool_version")
def fixture_tool_version(
    monkeypatch: pytest.MonkeyPatch,
) -> tools_models.DatabaseTool:
    version = tools_models.DatabaseVersion(
        id=0,
        name="test",
    )

    def get_exisiting_tool_version(
        *args, **kwargs
    ) -> tools_models.DatabaseTool:
        return version

    monkeypatch.setattr(
        tools_injectables,
        "get_exisiting_tool_version",
        get_exisiting_tool_version,
    )
    return version


@pytest.mark.usefixtures("tool_with_test_integration")
def test_session_creation_hook_is_called(
    monkeypatch: pytest.MonkeyPatch,
    db: orm.Session,
    user: users_models.DatabaseUser,
    mockoperator: MockOperator,
    session_hook: TestSessionHook,
):
    monkeypatch.setattr(
        sessions_routes,
        "start_persistent_guacamole_session",
        lambda *args, **kwargs: sessions_models.DatabaseSession(id="test"),
    )

    monkeypatch.setattr(
        sessions_routes,
        "get_image_for_tool_version",
        lambda *args, **kwargs: "placeholder",
    )

    sessions_routes.request_persistent_session(
        sessions_models.PostPersistentSessionRequest(tool_id=0, version_id=0),
        user,
        db,
        mockoperator,
    )

    assert session_hook.configuration_hook_counter == 1
    assert session_hook.post_creation_hook_counter == 1


def test_pre_termination_hook_is_called(
    monkeypatch: pytest.MonkeyPatch,
    mockoperator: MockOperator,
    session_hook: TestSessionHook,
    tool_with_test_integration: tools_models.DatabaseTool,
):
    monkeypatch.setattr(
        sessions_crud,
        "delete_session",
        lambda *args, **kwargs: None,
    )

    sessions_routes.end_session(
        sessions_models.PostPersistentSessionRequest(tool_id=0, version_id=0),
        sessions_models.DatabaseSession(tool=tool_with_test_integration),
        mockoperator,
    )

    session_hook.post_termination_hook_counter == 1
