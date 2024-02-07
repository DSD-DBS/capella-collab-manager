# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import typing as t
import uuid

import pytest
from sqlalchemy import orm

from capellacollab import __main__
from capellacollab.core import models as core_models
from capellacollab.projects import models as projects_models
from capellacollab.sessions import crud as sessions_crud
from capellacollab.sessions import hooks as sessions_hooks
from capellacollab.sessions import models as sessions_models
from capellacollab.sessions import operators
from capellacollab.sessions import routes as sessions_routes
from capellacollab.sessions.hooks import interface as hooks_interface
from capellacollab.sessions.operators import k8s
from capellacollab.sessions.operators import models as operators_models
from capellacollab.tools import injectables as tools_injectables
from capellacollab.tools import models as tools_models
from capellacollab.tools.integrations import models as tools_integration_models
from capellacollab.users import models as users_models


class MockOperator:
    # pylint: disable=unused-argument
    def start_session(self, *args, **kwargs) -> k8s.Session:
        return k8s.Session("test", {1}, datetime.datetime.now(), "test")

    def kill_session(self, *args, **kwargs) -> None:
        pass

    # pylint: disable=unused-argument
    def create_persistent_volume(self, *args, **kwargs):
        return


class TestSessionHook(hooks_interface.HookRegistration):
    configuration_hook_counter = 0
    post_creation_hook_counter = 0
    post_termination_hook_counter = 0

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

    __main__.app.dependency_overrides[
        operators.get_operator
    ] = get_mock_operator
    yield mock
    del __main__.app.dependency_overrides[operators.get_operator]


@pytest.fixture(autouse=True, name="tool")
def fixture_tool(
    monkeypatch: pytest.MonkeyPatch,
) -> tools_models.DatabaseTool:
    tool = tools_models.DatabaseTool(
        name="test",
        docker_image_template="test",
    )

    mock_integration = tools_integration_models.DatabaseToolIntegrations(
        tool=tool
    )
    tool.integrations = mock_integration

    # pylint: disable=unused-argument
    def mock_get_existing_tool(*args, **kwargs) -> tools_models.DatabaseTool:
        return tool

    monkeypatch.setattr(
        tools_injectables, "get_existing_tool", mock_get_existing_tool
    )
    return tool


@pytest.fixture(autouse=True, name="tool_version")
def fixture_tool_version(
    monkeypatch: pytest.MonkeyPatch, tool: tools_models.DatabaseTool
) -> tools_models.DatabaseVersion:
    version = tools_models.DatabaseVersion(
        name="test", is_recommended=False, is_deprecated=False, tool=tool
    )

    # pylint: disable=unused-argument
    def get_exisiting_tool_version(
        *args, **kwargs
    ) -> tools_models.DatabaseVersion:
        return version

    monkeypatch.setattr(
        tools_injectables,
        "get_exisiting_tool_version",
        get_exisiting_tool_version,
    )
    return version


@pytest.fixture(name="session")
def fixture_session(
    user: users_models.DatabaseUser,
    tool: tools_models.DatabaseTool,
    tool_version: tools_models.DatabaseVersion,
    project: projects_models.DatabaseProject,
) -> sessions_models.DatabaseSession:
    return sessions_models.DatabaseSession(
        str(uuid.uuid1()),
        ports=[1],
        created_at=datetime.datetime.now(),
        host="",
        type=sessions_models.WorkspaceType.PERSISTENT,
        environment={},
        rdp_password="",
        guacamole_username="",
        owner=user,
        tool=tool,
        version=tool_version,
        project=project,
    )


@pytest.mark.usefixtures("tool")
def test_session_creation_hook_is_called(
    monkeypatch: pytest.MonkeyPatch,
    db: orm.Session,
    user: users_models.DatabaseUser,
    mockoperator: MockOperator,
    session_hook: TestSessionHook,
    session: sessions_models.DatabaseSession,
):
    monkeypatch.setattr(
        sessions_routes,
        "start_persistent_guacamole_session",
        lambda *args, **kwargs: session,
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
        mockoperator,  # type: ignore
        "testuser",
    )

    assert session_hook.configuration_hook_counter == 1
    assert session_hook.post_creation_hook_counter == 1


def test_pre_termination_hook_is_called(
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

    sessions_routes.end_session(
        db,
        session,
        mockoperator,  # type: ignore
    )
