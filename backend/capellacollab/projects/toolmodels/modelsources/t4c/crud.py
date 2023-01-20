# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from sqlalchemy import select
from sqlalchemy.orm import Session

from capellacollab.projects.toolmodels.models import DatabaseCapellaModel
from capellacollab.projects.toolmodels.modelsources.t4c.models import (
    DatabaseT4CModel,
    SubmitT4CModel,
)
from capellacollab.settings.modelsources.t4c.repositories.models import (
    DatabaseT4CRepository,
)


def get_t4c_model_by_id(db: Session, t4c_model_id: int) -> DatabaseT4CModel:
    return db.execute(
        select(DatabaseT4CModel).where(DatabaseT4CModel.id == t4c_model_id)
    ).scalar_one()


def get_t4c_models(db) -> list[DatabaseT4CModel]:
    return db.execute(select(DatabaseT4CModel)).scalars().all()


def get_t4c_models_for_tool_model(
    db: Session, model: DatabaseCapellaModel
) -> list[DatabaseT4CModel]:
    return (
        db.execute(
            select(DatabaseT4CModel).where(DatabaseT4CModel.model == model)
        )
        .scalars()
        .all()
    )


def get_repository_model_t4c_models(
    db: Session, repository: DatabaseT4CRepository, model: DatabaseCapellaModel
) -> list[DatabaseT4CModel]:
    return (
        db.execute(
            select(DatabaseT4CModel)
            .where(DatabaseT4CModel.model == model)
            .where(DatabaseT4CModel.repository == repository)
        )
        .scalars()
        .all()
    )


def create_t4c_model(
    db: Session,
    model: DatabaseCapellaModel,
    repository: DatabaseT4CRepository,
    name: str,
) -> DatabaseT4CModel:
    t4c_model = DatabaseT4CModel(name=name, model=model, repository=repository)
    db.add(t4c_model)
    db.commit()
    return t4c_model


def patch_t4c_model(
    db: Session, t4c_model: DatabaseT4CModel, patch_model: SubmitT4CModel
) -> DatabaseT4CModel:
    for key in patch_model.dict():
        if value := getattr(patch_model, key):
            setattr(t4c_model, key, value)
    db.commit()
    return t4c_model


def set_repository_for_t4c_model(
    db: Session,
    t4c_model: DatabaseT4CModel,
    t4c_repository: DatabaseT4CRepository,
):
    t4c_model.repository = t4c_repository
    db.commit()


def delete_t4c_model(db: Session, t4c_model: DatabaseT4CModel):
    db.delete(t4c_model)
    db.commit()
