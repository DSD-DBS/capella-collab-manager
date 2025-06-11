# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import uuid

import pytest
from apscheduler import job as ap_job
from sqlalchemy import orm

from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.projects.toolmodels.backups import crud as pipelines_crud
from capellacollab.projects.toolmodels.backups import (
    interface as pipelines_interface,
)
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


@pytest.fixture(name="pipeline")
def fixture_pipeline(
    db: orm.Session,
    capella_model: toolmodels_models.DatabaseToolModel,
    git_model: git_models.DatabaseGitModel,
    t4c_model: t4c_models.DatabaseT4CModel,
    executor_name: str,
) -> pipelines_models.DatabasePipeline:
    pipeline = pipelines_models.DatabasePipeline(
        git_model=git_model,
        t4c_model=t4c_model,
        created_by=executor_name,
        model=capella_model,
        t4c_username="techuser-" + str(uuid.uuid4()),
        t4c_password="password",
        run_nightly=False,
    )
    return pipelines_crud.create_pipeline(db, pipeline)


@pytest.fixture(name="pipeline_scheduled")
def fixture_pipeline_scheduled(
    db: orm.Session,
    pipeline: pipelines_models.DatabasePipeline,
) -> ap_job.Job:
    pipeline.run_nightly = True
    return pipelines_interface.schedule_pipeline(db, pipeline)
