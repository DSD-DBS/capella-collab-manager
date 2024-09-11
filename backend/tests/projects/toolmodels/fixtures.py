# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from sqlalchemy import orm

import capellacollab.projects.models as projects_models
import capellacollab.projects.toolmodels.crud as toolmodels_crud
import capellacollab.projects.toolmodels.models as toolmodels_models
import capellacollab.tools.models as tools_models


@pytest.fixture(name="capella_model")
def fixture_capella_model(
    db: orm.Session,
    project: projects_models.DatabaseProject,
    capella_tool_version: tools_models.DatabaseVersion,
) -> toolmodels_models.DatabaseToolModel:
    model = toolmodels_models.PostToolModel(
        name="test", description="test", tool_id=capella_tool_version.tool.id
    )
    return toolmodels_crud.create_model(
        db, project, model, capella_tool_version.tool, capella_tool_version
    )


@pytest.fixture(name="jupyter_model")
def fixture_jupyter_model(
    db: orm.Session,
    project: projects_models.DatabaseProject,
    jupyter_tool: tools_models.DatabaseTool,
) -> toolmodels_models.DatabaseToolModel:
    jupyter_model = toolmodels_models.PostToolModel(
        name="Jupyter test", description="", tool_id=jupyter_tool.id
    )
    return toolmodels_crud.create_model(
        db,
        project,
        jupyter_model,
        tool=jupyter_tool,
        configuration={"workspace": "test"},
    )
