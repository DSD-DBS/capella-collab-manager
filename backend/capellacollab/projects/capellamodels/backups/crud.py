# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from sqlalchemy import select
from sqlalchemy.orm import Session

from capellacollab.projects.capellamodels.models import DatabaseCapellaModel

from .models import DatabaseBackup


def get_pipeline_by_id(db: Session, pipeline_id: int):
    return db.execute(
        select(DatabaseBackup).where(DatabaseBackup.id == pipeline_id)
    ).scalar_one()


def get_pipelines_for_model(
    db: Session, model: DatabaseCapellaModel
) -> list[DatabaseBackup]:
    return (
        db.execute(
            select(DatabaseBackup).where(DatabaseBackup.model_id == model.id)
        )
        .scalars()
        .all()
    )


def create_pipeline(db: Session, pipeline: DatabaseBackup):
    db.add(pipeline)
    db.commit()
    return pipeline


def delete_pipeline(db: Session, pipeline: DatabaseBackup):
    pipeline.delete()
    db.commit()


def get_pipeline_run_by_id(db: Session, pipeline: DatabaseBackup, run_id: int):
    raise NotImplementedError()
