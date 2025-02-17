# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import pytest

import capellacollab.projects.toolmodels.models as toolmodels_models
from capellacollab.sessions.hooks import interface as hooks_interface
from capellacollab.sessions.hooks import jupyter as jupyter_hook
from capellacollab.sessions.operators import models as operators_models
from capellacollab.tools import models as tools_models


@pytest.mark.usefixtures("project_user")
def test_jupyter_successful_volume_mount(
    jupyter_model: toolmodels_models.DatabaseToolModel,
    jupyter_tool: tools_models.DatabaseTool,
    configuration_hook_request: hooks_interface.ConfigurationHookRequest,
):
    class MockOperator:
    
        def persistent_volume_exists(self, name: str) -> bool:
            return True

    configuration_hook_request.operator = MockOperator()  # type: ignore
    configuration_hook_request.tool = jupyter_tool

    result = jupyter_hook.JupyterIntegration().configuration_hook(
        configuration_hook_request
    )

    assert not result["warnings"]
    assert len(result["volumes"]) == 1

    volume = result["volumes"][0]
    assert isinstance(volume, operators_models.PersistentVolume)
    assert (
        volume.volume_name
        == "shared-workspace-" + jupyter_model.configuration["workspace"]
    )


@pytest.mark.usefixtures("project_user", "jupyter_model")
def test_jupyter_volume_mount_not_found(
    jupyter_tool: tools_models.DatabaseTool,
    configuration_hook_request: hooks_interface.ConfigurationHookRequest,
):
    class MockOperator:
    
        def persistent_volume_exists(self, name: str) -> bool:
            return False

    configuration_hook_request.operator = MockOperator()  # type: ignore
    configuration_hook_request.tool = jupyter_tool

    result = jupyter_hook.JupyterIntegration().configuration_hook(
        configuration_hook_request
    )

    assert not result["volumes"]
    assert len(result["warnings"]) == 1
    assert (
        result["warnings"][0].err_code == "JUPYTER_FILE_SHARE_VOLUME_NOT_FOUND"
    )


@pytest.mark.usefixtures("jupyter_model")
def test_jupyter_volume_mount_without_project_access(
    jupyter_tool: tools_models.DatabaseTool,
    configuration_hook_request: hooks_interface.ConfigurationHookRequest,
):
    configuration_hook_request.tool = jupyter_tool

    result = jupyter_hook.JupyterIntegration().configuration_hook(
        configuration_hook_request
    )

    assert not result["volumes"]
    assert not result["warnings"]
