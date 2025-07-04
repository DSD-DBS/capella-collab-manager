# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
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
) -> models.DatabasePipeline | None:
    return db.execute(
        sa.select(models.DatabasePipeline).where(
            models.DatabasePipeline.id == pipeline_id
        )
    ).scalar_one_or_none()


def get_pipelines_for_tool_model(
    db: orm.Session, model: toolmodels_models.DatabaseToolModel
) -> abc.Sequence[models.DatabasePipeline]:
    return (
        db.execute(
            sa.select(models.DatabasePipeline).where(
                models.DatabasePipeline.model == model
            )
        )
        .scalars()
        .all()
    )


def get_all_pipelines(
    db: orm.Session,
) -> abc.Sequence[models.DatabasePipeline]:
    return db.execute(sa.select(models.DatabasePipeline)).scalars().all()


def get_first_pipeline_for_tool_model(
    db: orm.Session, model: toolmodels_models.DatabaseToolModel
) -> models.DatabasePipeline | None:
    return (
        db.execute(
            sa.select(models.DatabasePipeline).where(
                models.DatabasePipeline.model == model
            )
        )
        .scalars()
        .first()
    )


def get_pipelines_for_git_model(
    db: orm.Session, model: git_models.DatabaseGitModel
) -> abc.Sequence[models.DatabasePipeline]:
    return (
        db.execute(
            sa.select(models.DatabasePipeline).where(
                models.DatabasePipeline.git_model_id == model.id
            )
        )
        .scalars()
        .all()
    )


def get_pipelines_for_t4c_model(
    db: orm.Session, t4c_model: t4c_models.DatabaseT4CModel
) -> abc.Sequence[models.DatabasePipeline]:
    return (
        db.execute(
            sa.select(models.DatabasePipeline).where(
                models.DatabasePipeline.t4c_model_id == t4c_model.id
            )
        )
        .scalars()
        .all()
    )


def create_pipeline(
    db: orm.Session, pipeline: models.DatabasePipeline
) -> models.DatabasePipeline:
    db.add(pipeline)
    db.commit()
    return pipeline


def delete_pipeline(
    db: orm.Session, pipeline: models.DatabasePipeline
) -> None:
    db.delete(pipeline)
    db.commit()
