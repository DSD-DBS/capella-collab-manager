# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from sqlalchemy.orm import Session

from capellacollab.extensions.modelsources.t4c.models import DatabaseT4CModel


def get_t4c_model(db: Session, name: str, model_id: int):
    return (
        db.query(DatabaseT4CModel)
        .filter(DatabaseT4CModel.name == name)
        .filter(DatabaseT4CModel.model_id == model_id)
        .first()
    )


def get_t4c_model_by_id(db: Session, id: int, model_id: int):
    return (
        db.query(DatabaseT4CModel)
        .filter(DatabaseT4CModel.id == id)
        .filter(DatabaseT4CModel.model_id == model_id)
        .first()
    )


def get_all_t4c_models(db: Session, model_id: int):
    return (
        db.query(DatabaseT4CModel)
        .filter(DatabaseT4CModel.model_id == model_id)
        .all()
    )


def create_t4c_model(
    db: Session, model, repository, name: str
) -> DatabaseT4CModel:
    t4c_model = DatabaseT4CModel(name=name, model=model, repository=repository)
    db.add(t4c_model)
    db.commit()
    db.refresh(t4c_model)
    return t4c_model


def delete_project(db: Session, id: int, repo_name: str):
    db.query(DatabaseT4CModel).filter(DatabaseT4CModel.id == id).filter(
        DatabaseT4CModel.repository_name == repo_name
    ).delete()
    db.commit()
