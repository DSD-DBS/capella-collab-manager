# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from capellacollab.core.database import patch_database_with_pydantic_object
from capellacollab.projects.toolmodels.models import DatabaseCapellaModel
from capellacollab.projects.toolmodels.modelsources.t4c import models
from capellacollab.settings.modelsources.t4c.repositories.models import (
    DatabaseT4CRepository,
)


def get_t4c_model_by_id(
    db: Session, t4c_model_id: int
) -> models.DatabaseT4CModel | None:
    return db.execute(
        select(models.DatabaseT4CModel).where(
            models.DatabaseT4CModel.id == t4c_model_id
        )
    ).scalar_one_or_none()


def get_t4c_models(db: Session) -> Sequence[models.DatabaseT4CModel]:
    return db.execute(select(models.DatabaseT4CModel)).scalars().all()


def get_t4c_models_for_tool_model(
    db: Session, model: DatabaseCapellaModel
) -> Sequence[models.DatabaseT4CModel]:
    return (
        db.execute(
            select(models.DatabaseT4CModel).where(
                models.DatabaseT4CModel.model_id == model.id
            )
        )
        .scalars()
        .all()
    )


def create_t4c_model(
    db: Session,
    model: DatabaseCapellaModel,
    repository: DatabaseT4CRepository,
    name: str,
) -> models.DatabaseT4CModel:
    t4c_model = models.DatabaseT4CModel(
        name=name, model=model, repository=repository
    )
    db.add(t4c_model)
    db.commit()
    return t4c_model


def patch_t4c_model(
    db: Session,
    t4c_model: models.DatabaseT4CModel,
    patch_model: models.SubmitT4CModel,
) -> models.DatabaseT4CModel:
    patch_database_with_pydantic_object(t4c_model, patch_model)

    db.commit()
    return t4c_model


def delete_t4c_model(db: Session, t4c_model: models.DatabaseT4CModel):
    db.delete(t4c_model)
    db.commit()
