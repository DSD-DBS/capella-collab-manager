# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from sqlalchemy import orm

from capellacollab.projects import models as projects_models
from capellacollab.projects.toolmodels import crud as toolmodels_crud
from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.projects.toolmodels.restrictions import (
    crud as restrictions_crud,
)
from capellacollab.projects.toolmodels.restrictions import (
    models as restrictions_models,
)
from capellacollab.sessions import models as sessions_models
from capellacollab.sessions.hooks import interface as hooks_interface
from capellacollab.sessions.hooks import pure_variants
from capellacollab.tools import crud as tools_crud
from capellacollab.tools import models as tools_models


@pytest.fixture(name="pure_variants_tool")
def fixture_pure_variants_tool(
    db: orm.Session,
) -> tools_models.DatabaseTool:
    return tools_crud.create_tool(
        db,
        tools_models.CreateTool(
            name="test",
            integrations=tools_models.ToolIntegrations(pure_variants=True),
        ),
    )


@pytest.fixture(name="pure_variants_model")
def fixture_pure_variants_model(
    db: orm.Session,
    project: projects_models.DatabaseProject,
    pure_variants_tool: tools_models.DatabaseTool,
) -> toolmodels_models.DatabaseToolModel:
    return toolmodels_crud.create_model(
        db,
        project,
        post_model=toolmodels_models.PostToolModel(
            name="test", tool_id=pure_variants_tool.id
        ),
        tool=pure_variants_tool,
    )


def test_skip_for_read_only_sessions(
    configuration_hook_request: hooks_interface.ConfigurationHookRequest,
):
    """pure::variants has no read-only support

    Therefore, the hook also shouldn't do anything for read-only sessions.
    """
    configuration_hook_request.session_type = (
        sessions_models.SessionType.READONLY
    )
    result = pure_variants.PureVariantsIntegration().configuration_hook(
        configuration_hook_request
    )

    assert result == hooks_interface.ConfigurationHookResult()


@pytest.mark.usefixtures("project_user")
def test_skip_when_user_has_no_pv_access(
    db: orm.Session,
    pure_variants_model: toolmodels_models.DatabaseToolModel,
    configuration_hook_request: hooks_interface.ConfigurationHookRequest,
):
    """If a user has no access to a project with a model that
    has the pure::variants restriction enabled, skip loading of the license.
    """
    assert pure_variants_model.restrictions

    restrictions_crud.update_model_restrictions(
        db,
        pure_variants_model.restrictions,
        restrictions_models.ToolModelRestrictions(allow_pure_variants=False),
    )

    result = pure_variants.PureVariantsIntegration().configuration_hook(
        configuration_hook_request
    )

    assert "environment" not in result
    assert "volumes" not in result
    assert result["warnings"][0].err_code == "PV_MODEL_NOT_FOUND"


@pytest.mark.usefixtures("project_user")
def test_skip_when_license_server_not_configured(
    db: orm.Session,
    pure_variants_model: toolmodels_models.DatabaseToolModel,
    configuration_hook_request: hooks_interface.ConfigurationHookRequest,
):
    """If no pure::variants license is configured in the settings,
    skip loading of the license.
    """

    assert pure_variants_model.restrictions

    restrictions_crud.update_model_restrictions(
        db,
        pure_variants_model.restrictions,
        restrictions_models.ToolModelRestrictions(allow_pure_variants=True),
    )

    result = pure_variants.PureVariantsIntegration().configuration_hook(
        configuration_hook_request
    )

    assert "environment" not in result
    assert "volumes" not in result
    assert result["warnings"][0].err_code == "PV_LICENSE_SERVER_NOT_CONFIGURED"


@pytest.mark.usefixtures("project_user", "pure_variants_license")
def test_inject_pure_variants_license_information(
    db: orm.Session,
    pure_variants_model: toolmodels_models.DatabaseToolModel,
    configuration_hook_request: hooks_interface.ConfigurationHookRequest,
):
    """Test that the configured license information is properly
    injected in the session container.
    """

    assert pure_variants_model.restrictions

    restrictions_crud.update_model_restrictions(
        db,
        pure_variants_model.restrictions,
        restrictions_models.ToolModelRestrictions(allow_pure_variants=True),
    )

    result = pure_variants.PureVariantsIntegration().configuration_hook(
        configuration_hook_request
    )

    assert result["environment"] == {
        "PURE_VARIANTS_LICENSE_SERVER": "http://127.0.0.1:27000",
    }
    assert result["volumes"][0].name == "pure-variants"
    assert "warnings" not in result
