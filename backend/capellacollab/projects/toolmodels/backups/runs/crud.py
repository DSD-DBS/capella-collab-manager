# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from collections import abc

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models


def get_pipeline_run_by_id(
    db: Session, run_id: int
) -> models.DatabasePipelineRun | None:
    return db.execute(
        select(models.DatabasePipelineRun).where(
            models.DatabasePipelineRun.id == run_id
        )
    ).scalar_one_or_none()


def get_pipelines_runs_by_status(
    db: Session, status: models.PipelineRunStatus
) -> abc.Sequence[models.DatabasePipelineRun]:
    return (
        db.execute(
            select(models.DatabasePipelineRun).where(
                models.DatabasePipelineRun.status == status
            )
        )
        .scalars()
        .all()
    )


def get_scheduled_or_running_pipelines(
    db: Session,
) -> abc.Sequence[models.DatabasePipelineRun]:
    return (
        db.execute(
            select(models.DatabasePipelineRun).where(
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
    db: Session, pipeline_run: models.DatabasePipelineRun
) -> models.DatabasePipelineRun:
    db.add(pipeline_run)
    db.commit()
    return pipeline_run
