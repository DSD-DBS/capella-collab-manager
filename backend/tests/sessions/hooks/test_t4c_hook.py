# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import json

import pytest
import responses
from sqlalchemy import orm

import capellacollab.settings.modelsources.t4c.instance.repositories.models as settings_t4c_repositories_models
from capellacollab.projects import models as projects_models
from capellacollab.projects.toolmodels import crud as toolmodels_crud
from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.projects.toolmodels.modelsources.t4c import (
    crud as models_t4c_crud,
)
from capellacollab.projects.users import models as projects_users_models
from capellacollab.sessions import models as sessions_models
from capellacollab.sessions.hooks import interface as sessions_hooks_interface
from capellacollab.sessions.hooks import t4c
from capellacollab.settings.modelsources.t4c.instance import (
    models as t4c_models,
)
from capellacollab.tools import crud as tools_crud
from capellacollab.tools import models as tools_models
from capellacollab.users import crud as users_crud
from capellacollab.users import models as users_models


@pytest.fixture(name="mock_add_user_to_repository")
def fixture_mock_add_user_to_repository(
    t4c_instance: t4c_models.DatabaseT4CInstance,
) -> responses.BaseResponse:
    return responses.add(
        responses.POST,
        f"{t4c_instance.rest_api}/users?repositoryName=test",
        status=200,
        json={},
    )


@pytest.fixture(name="mock_add_user_to_repository_failed")
def fixture_mock_add_user_to_repository_failed(
    t4c_instance: t4c_models.DatabaseT4CInstance,
) -> responses.BaseResponse:
    return responses.add(
        responses.POST,
        f"{t4c_instance.rest_api}/users?repositoryName=test",
        status=500,
    )


@responses.activate
@pytest.mark.usefixtures("t4c_model", "project_user")
def test_t4c_configuration_hook(
    user: users_models.DatabaseUser,
    mock_add_user_to_repository: responses.BaseResponse,
    configuration_hook_request: sessions_hooks_interface.ConfigurationHookRequest,
):
    result = t4c.T4CIntegration().configuration_hook(
        configuration_hook_request
    )

    assert result["environment"]["T4C_LICENCE_SECRET"]
    assert len(json.loads(result["environment"]["T4C_JSON"])) == 1
    assert result["environment"]["T4C_USERNAME"] == user.name
    assert result["environment"]["T4C_PASSWORD"]
    assert not result["warnings"]
    assert mock_add_user_to_repository.call_count == 1


@responses.activate
@pytest.mark.usefixtures("t4c_model", "admin")
def test_t4c_configuration_hook_as_admin(
    mock_add_user_to_repository: responses.BaseResponse,
    configuration_hook_request: sessions_hooks_interface.ConfigurationHookRequest,
):
    result = t4c.T4CIntegration().configuration_hook(
        configuration_hook_request
    )

    assert result["environment"]["T4C_LICENCE_SECRET"]
    assert len(json.loads(result["environment"]["T4C_JSON"])) == 1
    assert (
        result["environment"]["T4C_USERNAME"]
        == configuration_hook_request.user.name
    )
    assert result["environment"]["T4C_PASSWORD"]
    assert not result["warnings"]
    assert mock_add_user_to_repository.call_count == 1


@responses.activate
@pytest.mark.usefixtures("t4c_model", "admin")
def test_t4c_configuration_hook_with_same_repository_used_twice(
    db: orm.Session,
    project: projects_models.DatabaseProject,
    capella_tool_version: tools_models.DatabaseVersion,
    mock_add_user_to_repository: responses.BaseResponse,
    t4c_repository: settings_t4c_repositories_models.DatabaseT4CRepository,
    configuration_hook_request: sessions_hooks_interface.ConfigurationHookRequest,
):
    model = toolmodels_models.PostToolModel(
        name="test2", description="test", tool_id=capella_tool_version.tool.id
    )
    db_model = toolmodels_crud.create_model(
        db, project, model, capella_tool_version.tool, capella_tool_version
    )
    models_t4c_crud.create_t4c_model(db, db_model, t4c_repository, "default2")
    result = t4c.T4CIntegration().configuration_hook(
        configuration_hook_request
    )

    assert len(json.loads(result["environment"]["T4C_JSON"])) == 1
    assert not result["warnings"]
    assert mock_add_user_to_repository.call_count == 1


@responses.activate
@pytest.mark.usefixtures("t4c_model", "project_user")
def test_t4c_configuration_hook_failure(
    user: users_models.DatabaseUser,
    mock_add_user_to_repository_failed: responses.BaseResponse,
    configuration_hook_request: sessions_hooks_interface.ConfigurationHookRequest,
):
    """Test behavior when T4C API call fails"""

    result = t4c.T4CIntegration().configuration_hook(
        configuration_hook_request
    )

    assert result["environment"]["T4C_LICENCE_SECRET"]
    assert len(json.loads(result["environment"]["T4C_JSON"])) == 1
    assert len(result["warnings"]) == 1
    assert result["environment"]["T4C_USERNAME"] == user.name
    assert result["environment"]["T4C_PASSWORD"]
    assert mock_add_user_to_repository_failed.call_count == 1


@responses.activate
@pytest.mark.usefixtures("t4c_model", "project_user")
def test_configuration_hook_for_archived_project(
    project: projects_models.DatabaseProject,
    db: orm.Session,
    user: users_models.DatabaseUser,
    mock_add_user_to_repository: responses.BaseResponse,
    configuration_hook_request: sessions_hooks_interface.ConfigurationHookRequest,
):
    project.is_archived = True
    db.commit()

    result = t4c.T4CIntegration().configuration_hook(
        configuration_hook_request
    )

    assert not result["environment"]["T4C_LICENCE_SECRET"]
    assert len(json.loads(result["environment"]["T4C_JSON"])) == 0
    assert result["environment"]["T4C_USERNAME"] == user.name
    assert result["environment"]["T4C_PASSWORD"]
    assert not result["warnings"]
    assert mock_add_user_to_repository.call_count == 0


@responses.activate
@pytest.mark.usefixtures("t4c_model", "project_user")
def test_configuration_hook_as_rw_user(
    db: orm.Session,
    user: users_models.DatabaseUser,
    mock_add_user_to_repository: responses.BaseResponse,
    project_user: projects_users_models.ProjectUserAssociation,
    configuration_hook_request: sessions_hooks_interface.ConfigurationHookRequest,
):
    project_user.permission = projects_users_models.ProjectUserPermission.READ
    db.commit()

    result = t4c.T4CIntegration().configuration_hook(
        configuration_hook_request
    )

    assert not result["environment"]["T4C_LICENCE_SECRET"]
    assert len(json.loads(result["environment"]["T4C_JSON"])) == 0
    assert result["environment"]["T4C_USERNAME"] == user.name
    assert result["environment"]["T4C_PASSWORD"]
    assert not result["warnings"]
    assert mock_add_user_to_repository.call_count == 0


@responses.activate
@pytest.mark.usefixtures("t4c_model", "project_user")
def test_configuration_hook_for_compatible_tool(
    db: orm.Session,
    user: users_models.DatabaseUser,
    capella_tool_version: tools_models.DatabaseVersion,
    mock_add_user_to_repository: responses.BaseResponse,
    configuration_hook_request: sessions_hooks_interface.ConfigurationHookRequest,
):
    custom_tool = tools_crud.create_tool(
        db, tools_models.CreateTool(name="custom")
    )
    create_compatible_tool_version = tools_models.CreateToolVersion(
        name="compatible_tool_version",
        config=tools_models.ToolVersionConfiguration(
            compatible_versions=[capella_tool_version.id]
        ),
    )
    compatible_tool_version = tools_crud.create_version(
        db, custom_tool, create_compatible_tool_version
    )

    configuration_hook_request.tool_version = compatible_tool_version
    result = t4c.T4CIntegration().configuration_hook(
        configuration_hook_request
    )

    assert result["environment"]["T4C_LICENCE_SECRET"]
    assert len(json.loads(result["environment"]["T4C_JSON"])) == 1
    assert result["environment"]["T4C_USERNAME"] == user.name
    assert result["environment"]["T4C_PASSWORD"]
    assert not result["warnings"]
    assert mock_add_user_to_repository.call_count == 1


def test_t4c_configuration_hook_non_persistent(
    configuration_hook_request: sessions_hooks_interface.ConfigurationHookRequest,
):
    configuration_hook_request.session_type = (
        sessions_models.SessionType.READONLY
    )
    result = t4c.T4CIntegration().configuration_hook(
        configuration_hook_request
    )

    assert result == sessions_hooks_interface.ConfigurationHookResult()


def test_t4c_connection_hook_non_persistent(
    session: sessions_models.DatabaseSession,
    session_connection_hook_request: sessions_hooks_interface.SessionConnectionHookRequest,
):
    session.type = sessions_models.SessionType.READONLY
    result = t4c.T4CIntegration().session_connection_hook(
        session_connection_hook_request
    )

    assert result == sessions_hooks_interface.SessionConnectionHookResult()


def test_t4c_connection_hook_shared_session(
    db: orm.Session,
    session: sessions_models.DatabaseSession,
    session_connection_hook_request: sessions_hooks_interface.SessionConnectionHookRequest,
):
    user2 = users_crud.create_user(
        db,
        "shared_with_user",
        "shared_with_user",
        None,
        users_models.Role.USER,
    )
    session.owner = user2
    result = t4c.T4CIntegration().session_connection_hook(
        session_connection_hook_request
    )

    assert result == sessions_hooks_interface.SessionConnectionHookResult()


def test_t4c_connection_hook(
    session: sessions_models.DatabaseSession,
    session_connection_hook_request: sessions_hooks_interface.SessionConnectionHookRequest,
):
    session.environment = {"T4C_PASSWORD": "test"}
    result = t4c.T4CIntegration().session_connection_hook(
        session_connection_hook_request
    )

    assert result["t4c_token"] == "test"


@responses.activate
@pytest.mark.usefixtures("t4c_model", "project_user")
def test_t4c_termination_hook(
    session: sessions_models.DatabaseSession,
    user: users_models.DatabaseUser,
    t4c_instance: t4c_models.DatabaseT4CInstance,
    capella_tool_version: tools_models.DatabaseVersion,
    pre_session_termination_hook_request: sessions_hooks_interface.PreSessionTerminationHookRequest,
):
    session.version = capella_tool_version
    pre_session_termination_hook_request.session = session
    rsp = responses.delete(
        f"{t4c_instance.rest_api}/users/{user.name}?repositoryName=test",
        status=200,
    )

    t4c.T4CIntegration().pre_session_termination_hook(
        pre_session_termination_hook_request
    )

    assert rsp.call_count == 1
