# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from collections import abc

import sqlalchemy as sa
from sqlalchemy import orm

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


def create_pipeline_run(
    db: orm.Session, pipeline_run: models.DatabasePipelineRun
) -> models.DatabasePipelineRun:
    db.add(pipeline_run)
    db.commit()
    return pipeline_run
