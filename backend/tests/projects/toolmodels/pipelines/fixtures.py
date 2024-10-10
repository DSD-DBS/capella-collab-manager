# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from sqlalchemy import orm

from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.projects.toolmodels.backups import crud as pipelines_crud
from capellacollab.projects.toolmodels.backups import (
    models as pipelines_models,
)
from capellacollab.projects.toolmodels.modelsources.git import (
    models as git_models,
)
from capellacollab.projects.toolmodels.modelsources.t4c import (
    models as t4c_models,
)


@pytest.fixture(name="run_nightly", params=[True, False])
def fixture_run_nightly(
    request: pytest.FixtureRequest,
):
    return request.param


@pytest.fixture(name="include_commit_history", params=[True, False])
def fixture_include_commit_history(
    request: pytest.FixtureRequest,
):
    return request.param


@pytest.fixture(name="pipeline")
def fixture_pipeline(
    db: orm.Session,
    capella_model: toolmodels_models.DatabaseToolModel,
    git_model: git_models.DatabaseGitModel,
    t4c_model: t4c_models.DatabaseT4CModel,
    executor_name: str,
    run_nightly: bool,
    include_commit_history: bool,
) -> pipelines_models.DatabaseBackup:
    pipeline = pipelines_models.DatabaseBackup(
        k8s_cronjob_id="unavailable",
        git_model=git_model,
        t4c_model=t4c_model,
        created_by=executor_name,
        model=capella_model,
        t4c_username="no",
        t4c_password="no",
        include_commit_history=include_commit_history,
        run_nightly=run_nightly,
    )
    return pipelines_crud.create_pipeline(db, pipeline)
