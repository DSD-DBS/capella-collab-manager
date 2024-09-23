# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from sqlalchemy import orm

import capellacollab.projects.toolmodels.models as toolmodels_models
import capellacollab.projects.toolmodels.modelsources.git.crud as project_git_crud
import capellacollab.projects.toolmodels.modelsources.git.models as project_git_models
import capellacollab.projects.toolmodels.modelsources.t4c.crud as models_t4c_crud
import capellacollab.projects.toolmodels.modelsources.t4c.models as models_t4c_models
import capellacollab.settings.modelsources.t4c.instance.repositories.models as settings_t4c_repositories_models


@pytest.fixture(name="t4c_model")
def fixture_t4c_model(
    db: orm.Session,
    capella_model: toolmodels_models.DatabaseToolModel,
    t4c_repository: settings_t4c_repositories_models.DatabaseT4CRepository,
) -> models_t4c_models.DatabaseT4CModel:
    return models_t4c_crud.create_t4c_model(
        db, capella_model, t4c_repository, "default"
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
