# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from collections import abc

import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.projects.toolmodels.modelsources.t4c import models
from capellacollab.settings.modelsources.t4c.instance.repositories import (
    models as repositories_models,
)


def get_t4c_model_by_id(
    db: orm.Session, t4c_model_id: int
) -> models.DatabaseT4CModel | None:
    return db.execute(
        sa.select(models.DatabaseT4CModel).where(
            models.DatabaseT4CModel.id == t4c_model_id
        )
    ).scalar_one_or_none()


def get_t4c_models(db: orm.Session) -> abc.Sequence[models.DatabaseT4CModel]:
    return db.execute(sa.select(models.DatabaseT4CModel)).scalars().all()


def get_t4c_models_for_tool_model(
    db: orm.Session, model: toolmodels_models.DatabaseToolModel
) -> abc.Sequence[models.DatabaseT4CModel]:
    return (
        db.execute(
            sa.select(models.DatabaseT4CModel).where(
                models.DatabaseT4CModel.model_id == model.id
            )
        )
        .scalars()
        .all()
    )


def create_t4c_model(
    db: orm.Session,
    model: toolmodels_models.DatabaseToolModel,
    repository: repositories_models.DatabaseT4CRepository,
    name: str,
) -> models.DatabaseT4CModel:
    t4c_model = models.DatabaseT4CModel(
        name=name, model=model, repository=repository
    )
    db.add(t4c_model)
    db.commit()
    return t4c_model


def patch_t4c_model(
    db: orm.Session,
    t4c_model: models.DatabaseT4CModel,
    repository: repositories_models.DatabaseT4CRepository,
    name: str | None = None,
) -> models.DatabaseT4CModel:
    if name is not None:
        t4c_model.name = name
    t4c_model.repository = repository
    db.commit()
    return t4c_model


def delete_t4c_model(db: orm.Session, t4c_model: models.DatabaseT4CModel):
    db.delete(t4c_model)
    db.commit()
