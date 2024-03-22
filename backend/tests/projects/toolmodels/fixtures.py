# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import uuid

import pytest
from sqlalchemy import orm

import capellacollab.projects.models as projects_models
import capellacollab.projects.toolmodels.crud as toolmodels_crud
import capellacollab.projects.toolmodels.models as toolmodels_models
import capellacollab.projects.toolmodels.modelsources.git.crud as project_git_crud
import capellacollab.projects.toolmodels.modelsources.git.models as project_git_models
import capellacollab.tools.models as tools_models


@pytest.fixture(name="capella_model")
def fixture_capella_model(
    db: orm.Session,
    project: projects_models.DatabaseProject,
    capella_tool_version: tools_models.DatabaseVersion,
) -> toolmodels_models.DatabaseToolModel:
    model = toolmodels_models.PostCapellaModel(
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
    jupyter_model = toolmodels_models.PostCapellaModel(
        name="Jupyter test",
        description="",
        tool_id=jupyter_tool.id,
        configuration={"workspace": str(uuid.uuid4())},
    )
    return toolmodels_crud.create_model(
        db,
        project,
        jupyter_model,
        tool=jupyter_tool,
        configuration={"workspace": "test"},
    )


@pytest.fixture(name="git_model")
def fixture_git_model(
    db: orm.Session, capella_model: toolmodels_models.DatabaseToolModel
) -> project_git_models.DatabaseGitModel:
    git_model = project_git_models.PostGitModel(
        path="https://example.com/test/project",
        entrypoint="test/test.aird",
        revision="main",
        username="user",
        password="password",
    )
    return project_git_crud.add_git_model_to_capellamodel(
        db, capella_model, git_model
    )
