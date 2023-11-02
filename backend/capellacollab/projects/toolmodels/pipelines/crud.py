# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from collections import abc

import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.projects.toolmodels.modelsources.git import (
    models as git_models,
)
from capellacollab.projects.toolmodels.modelsources.t4c import (
    models as t4c_models,
)

from . import models


def get_pipeline_by_id(
    db: orm.Session, pipeline_id: int
) -> models.DatabaseBackup | None:
    return db.execute(
        sa.select(models.DatabaseBackup).where(
            models.DatabaseBackup.id == pipeline_id
        )
    ).scalar_one_or_none()


def get_pipelines_for_tool_model(
    db: orm.Session, model: toolmodels_models.DatabaseCapellaModel
) -> abc.Sequence[models.DatabaseBackup]:
    return (
        db.execute(
            sa.select(models.DatabaseBackup).where(
                models.DatabaseBackup.model == model
            )
        )
        .scalars()
        .all()
    )


def get_first_pipeline_for_tool_model(
    db: orm.Session, model: toolmodels_models.DatabaseCapellaModel
) -> models.DatabaseBackup | None:
    return (
        db.execute(
            sa.select(models.DatabaseBackup).where(
                models.DatabaseBackup.model == model
            )
        )
        .scalars()
        .first()
    )


def get_pipelines_for_git_model(
    db: orm.Session, model: git_models.DatabaseGitModel
) -> abc.Sequence[models.DatabaseBackup]:
    return (
        db.execute(
            sa.select(models.DatabaseBackup).where(
                models.DatabaseBackup.git_model_id == model.id  # type: ignore # FIXME: git_model_id doesn't exist anymore
            )
        )
        .scalars()
        .all()
    )


def get_pipelines_for_t4c_model(
    db: orm.Session, t4c_model: t4c_models.DatabaseT4CModel
) -> abc.Sequence[models.DatabaseBackup]:
    return (
        db.execute(
            sa.select(models.DatabaseBackup).where(
                models.DatabaseBackup.t4c_model_id == t4c_model.id  # type: ignore # FIXME: git_model_id doesn't exist anymore
            )
        )
        .scalars()
        .all()
    )


def create_pipeline(
    db: orm.Session, pipeline: models.DatabaseBackup
) -> models.DatabaseBackup:
    db.add(pipeline)
    db.commit()
    return pipeline


def delete_pipeline(db: orm.Session, pipeline: models.DatabaseBackup) -> None:
    db.delete(pipeline)
    db.commit()
