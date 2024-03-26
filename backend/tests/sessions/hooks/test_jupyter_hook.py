# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import pytest
from sqlalchemy import orm

import capellacollab.projects.toolmodels.models as toolmodels_models
from capellacollab.sessions.hooks import jupyter as jupyter_hook
from capellacollab.tools import models as tools_models
from capellacollab.users import models as users_models


@pytest.mark.usefixtures("project_user")
def test_jupyter_successful_volume_mount(
    jupyter_model: toolmodels_models.DatabaseToolModel,
    jupyter_tool: tools_models.DatabaseTool,
    user: users_models.DatabaseUser,
    db: orm.Session,
):
    class MockOperator:
        def persistent_volume_exists(self, name: str) -> bool:
            return True

    result = jupyter_hook.JupyterIntegration().configuration_hook(
        db=db, user=user, tool=jupyter_tool, operator=MockOperator()
    )

    assert not result["warnings"]
    assert len(result["volumes"]) == 1
    assert (
        result["volumes"][0].volume_name
        == "shared-workspace-" + jupyter_model.configuration["workspace"]
    )


@pytest.mark.usefixtures("project_user", "jupyter_model")
def test_jupyter_volume_mount_not_found(
    jupyter_tool: tools_models.DatabaseTool,
    user: users_models.DatabaseUser,
    db: orm.Session,
):
    class MockOperator:
        def persistent_volume_exists(self, name: str) -> bool:
            return False

    result = jupyter_hook.JupyterIntegration().configuration_hook(
        db=db, user=user, tool=jupyter_tool, operator=MockOperator()
    )

    assert not result["volumes"]
    assert len(result["warnings"]) == 1
    assert (
        result["warnings"][0].err_code == "JUPYTER_FILE_SHARE_VOLUME_NOT_FOUND"
    )


@pytest.mark.usefixtures("jupyter_model")
def test_jupyter_volume_mount_without_project_access(
    jupyter_tool: tools_models.DatabaseTool,
    user: users_models.DatabaseUser,
    db: orm.Session,
):
    class MockOperator:
        pass

    result = jupyter_hook.JupyterIntegration().configuration_hook(
        db=db, user=user, tool=jupyter_tool, operator=MockOperator()
    )

    assert not result["volumes"]
    assert not result["warnings"]
