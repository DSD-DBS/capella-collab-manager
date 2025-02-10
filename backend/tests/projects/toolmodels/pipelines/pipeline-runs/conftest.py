# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime

import pytest
from sqlalchemy import orm

import capellacollab.projects.toolmodels.backups.models as pipeline_models
import capellacollab.projects.toolmodels.backups.runs.crud as pipeline_runs_crud
import capellacollab.projects.toolmodels.backups.runs.models as pipeline_runs_models
import capellacollab.projects.users.models as projects_users_models


@pytest.fixture(name="pipeline_run")
def fixture_pipeline_run(
    db: orm.Session,
    pipeline: pipeline_models.DatabaseBackup,
    project_manager: projects_users_models.DatabaseProjectUserAssociation,
) -> pipeline_runs_models.DatabasePipelineRun:
    pipeline_run = pipeline_runs_models.DatabasePipelineRun(
        reference_id="undefined",
        status=pipeline_runs_models.PipelineRunStatus.PENDING,
        pipeline=pipeline,
        triggerer=project_manager.user,
        trigger_time=datetime.datetime.now(datetime.UTC),
        logs_last_fetched_timestamp=None,
        environment={},
    )
    return pipeline_runs_crud.create_pipeline_run(db, pipeline_run)
