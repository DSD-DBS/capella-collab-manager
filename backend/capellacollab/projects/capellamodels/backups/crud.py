# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from select import select

from sqlalchemy.orm import Session

from capellacollab.projects.capellamodels.models import DatabaseCapellaModel

from .models import DB_EASEBackup


def get_pipeline_by_id(db: Session, pipeline_id: int):
    return db.execute(
        select(DB_EASEBackup).where(DB_EASEBackup.id == pipeline_id)
    ).scalar_one()


def get_pipelines_for_model(
    db: Session, model: DatabaseCapellaModel
) -> list[DB_EASEBackup]:
    return (
        db.execute(
            select(DB_EASEBackup).where(DB_EASEBackup.model_id == model.id)
        )
        .scalars()
        .all()
    )


def create_pipeline(db: Session, pipeline: DB_EASEBackup):
    db.add(pipeline)
    db.commit()
    return pipeline


def delete_pipeline(db: Session, pipeline: DB_EASEBackup):
    pipeline.delete()
    db.commit()


def get_pipeline_run_by_id(db: Session, pipeline: DB_EASEBackup, run_id: int):
    raise NotImplementedError()
