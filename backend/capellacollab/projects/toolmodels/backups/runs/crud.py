# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models


def get_pipeline_run_by_id(
    db: Session, run_id: str
) -> models.DatabasePipelineRun | None:
    return db.execute(
        select(models.DatabasePipelineRun).where(
            models.DatabasePipelineRun.id == run_id
        )
    ).scalar_one_or_none()


def get_all_pipelines_runs_by_status(
    db: Session, status: models.PipelineRunStatus
) -> list[models.DatabasePipelineRun]:
    return (
        db.execute(
            select(models.DatabasePipelineRun).where(
                models.DatabasePipelineRun.status == status
            )
        )
        .scalars()
        .all()
    )


def get_scheduled_and_running_pipelines(
    db: Session,
) -> list[models.DatabasePipelineRun]:
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


def create_pipeline_run(db: Session, pipeline_run: models.DatabasePipelineRun):
    db.add(pipeline_run)
    db.commit()
    return pipeline_run
