# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from sqlalchemy.orm import Session

from capellacollab.extensions.modelsources.t4c.models import DB_T4CModel


def get_t4c_model(db: Session, name: str, model_id: int):
    return (
        db.query(DB_T4CModel)
        .filter(DB_T4CModel.name == name)
        .filter(DB_T4CModel.model_id == model_id)
        .first()
    )


def get_t4c_model_by_id(db: Session, id: int, model_id: int):
    return (
        db.query(DB_T4CModel)
        .filter(DB_T4CModel.id == id)
        .filter(DB_T4CModel.model_id == model_id)
        .first()
    )


def get_all_t4c_models(db: Session, model_id: int):
    return db.query(DB_T4CModel).filter(DB_T4CModel.model_id == model_id).all()


def create_t4c_model(db: Session, model_id: int, project_name: str):
    project = DB_T4CModel(model_id=model_id, name=project_name)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, id: int, repo_name: str):
    db.query(DB_T4CModel).filter(DB_T4CModel.id == id).filter(
        DB_T4CModel.repository_name == repo_name
    ).delete()
    db.commit()
