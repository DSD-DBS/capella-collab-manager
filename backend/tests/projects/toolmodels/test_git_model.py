# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from sqlalchemy import orm

import capellacollab.projects.toolmodels.modelsources.git.crud as project_git_crud
import capellacollab.projects.toolmodels.modelsources.git.models as project_git_models


def test_reset_repository_id_on_git_model_path_change(
    db: orm.Session,
    git_model: project_git_models.DatabaseGitModel,
):
    assert git_model.repository_id is None

    project_git_crud.update_git_model_repository_id(db, git_model, "1")

    assert git_model.repository_id == "1"

    put_git_model = project_git_models.PutGitModel.model_validate(git_model)
    put_git_model.path = "random-new-path"

    project_git_crud.update_git_model(db, git_model, put_git_model)

    assert git_model.path == "random-new-path"
    assert git_model.repository_id is None
