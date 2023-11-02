# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from collections import abc

import fastapi_pagination.ext.sqlalchemy
import sqlalchemy as sa
from sqlalchemy import orm

from .. import models as pipeline_models
from . import models


def get_pipeline_run_by_id(
    db: orm.Session, run_id: int
) -> models.DatabasePipelineRun | None:
    return db.execute(
        sa.select(models.DatabasePipelineRun).where(
            models.DatabasePipelineRun.id == run_id
        )
    ).scalar_one_or_none()


def get_pipelines_runs_by_status(
    db: orm.Session, status: models.PipelineRunStatus
) -> abc.Sequence[models.DatabasePipelineRun]:
    return (
        db.execute(
            sa.select(models.DatabasePipelineRun).where(
                models.DatabasePipelineRun.status == status
            )
        )
        .scalars()
        .all()
    )


def get_scheduled_or_running_pipelines(
    db: orm.Session,
) -> abc.Sequence[models.DatabasePipelineRun]:
    return (
        db.execute(
            sa.select(models.DatabasePipelineRun).where(
                (
                    models.DatabasePipelineRun.status
                    == models.PipelineRunStatus.RUNNING
                )
                | (
                    models.DatabasePipelineRun.status
                    == models.PipelineRunStatus.SCHEDULED
                )
            )
        )
        .scalars()
        .all()
    )


def get_pipeline_runs_for_pipeline_id_paginated(
    db: orm.Session, pipeline: pipeline_models.DatabaseBackup
) -> fastapi_pagination.Page[models.PipelineRun]:
    return fastapi_pagination.ext.sqlalchemy.paginate(
        db,
        sa.select(models.DatabasePipelineRun)
        .where(models.DatabasePipelineRun.pipeline == pipeline)
        .order_by(models.DatabasePipelineRun.id.desc()),
    )


def create_pipeline_run(
    db: orm.Session, pipeline_run: models.DatabasePipelineRun
) -> models.DatabasePipelineRun:
    db.add(pipeline_run)
    db.commit()
    return pipeline_run


def get_last_pipeline_run_of_pipeline(
    db: orm.Session, pipeline: pipeline_models.DatabaseBackup
) -> models.DatabasePipelineRun | None:
    return (
        db.execute(
            sa.select(models.DatabasePipelineRun)
            .where(models.DatabasePipelineRun.pipeline == pipeline)
            .order_by(models.DatabasePipelineRun.id.desc())
        )
        .scalars()
        .first()
    )
