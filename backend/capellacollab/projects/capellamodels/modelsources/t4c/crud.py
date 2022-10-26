# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from sqlalchemy import select
from sqlalchemy.orm import Session

from capellacollab.projects.capellamodels.models import DatabaseCapellaModel
from capellacollab.projects.capellamodels.modelsources.t4c.models import (
    DatabaseT4CModel,
    SubmitT4CModel,
    T4CRepositoryWithModels,
)
from capellacollab.settings.modelsources.t4c.repositories.models import (
    DatabaseT4CRepository,
)


def get_t4c_model_by_id(db: Session, t4c_model_id: int) -> DatabaseT4CModel:
    return db.execute(
        select(DatabaseT4CModel).where(DatabaseT4CModel.id == t4c_model_id)
    ).scalar_one()


def get_all_t4c_models(
    db: Session, model: DatabaseCapellaModel
) -> list[DatabaseT4CModel]:
    return (
        db.execute(
            select(DatabaseT4CModel).where(DatabaseT4CModel.model == model)
        )
        .scalars()
        .all()
    )


def create_t4c_model(
    db: Session, model, repository, name: str
) -> DatabaseT4CModel:
    t4c_model = DatabaseT4CModel(name=name, model=model, repository=repository)
    db.add(t4c_model)
    db.commit()
    return t4c_model


def patch_t4c_model(
    db: Session,
    t4c_model: DatabaseT4CModel,
    patch_model: SubmitT4CModel,
) -> DatabaseT4CModel:
    for key in patch_model.dict():
        if value := patch_model.__getattribute__(key):
            t4c_model.__setattr__(key, value)
    db.add(t4c_model)
    db.commit()
    return t4c_model
