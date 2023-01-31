# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from sqlalchemy import select
from sqlalchemy.orm import Session

from capellacollab.projects.toolmodels.models import DatabaseCapellaModel
from capellacollab.projects.toolmodels.modelsources.git.models import (
    DatabaseGitModel,
)
from capellacollab.projects.toolmodels.modelsources.t4c import (
    models as t4c_models,
)

from . import models


def get_pipeline_by_id(db: Session, pipeline_id: int) -> models.DatabaseBackup:
    return db.execute(
        select(models.DatabaseBackup).where(
            models.DatabaseBackup.id == pipeline_id
        )
    ).scalar_one()


def get_pipelines_for_model(
    db: Session, model: DatabaseCapellaModel
) -> list[models.DatabaseBackup]:
    return (
        db.execute(
            select(models.DatabaseBackup).where(
                models.DatabaseBackup.model_id == model.id
            )
        )
        .scalars()
        .all()
    )


def get_pipelines_for_git_model(
    db: Session, model: DatabaseGitModel
) -> list[models.DatabaseBackup]:
    return (
        db.execute(
            select(models.DatabaseBackup).where(
                models.DatabaseBackup.git_model_id == model.id
            )
        )
        .scalars()
        .all()
    )


def get_pipelines_for_t4c_model(
    db: Session, t4c_model: t4c_models.DatabaseT4CModel
) -> list[models.DatabaseBackup]:
    return (
        db.execute(
            select(models.DatabaseBackup).where(
                models.DatabaseBackup.t4c_model_id == t4c_model.id
            )
        )
        .scalars()
        .all()
    )


def create_pipeline(db: Session, pipeline: models.DatabaseBackup):
    db.add(pipeline)
    db.commit()
    return pipeline


def delete_pipeline(db: Session, pipeline: models.DatabaseBackup):
    db.delete(pipeline)
    db.commit()


def get_pipeline_run_by_id(
    db: Session, pipeline: models.DatabaseBackup, run_id: int
):
    raise NotImplementedError()
