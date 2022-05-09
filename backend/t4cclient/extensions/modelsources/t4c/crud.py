# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from sqlalchemy.orm import Session
from t4cclient.extensions.modelsources.t4c.models import DatabaseT4CModel


def get_project(db: Session, name: str, repo_name: str):
    return (
        db.query(DatabaseT4CModel)
        .filter(DatabaseT4CModel.name == name)
        .filter(DatabaseT4CModel.repository_name == repo_name)
        .first()
    )


def get_project_by_id(db: Session, id: int, repo_name: str):
    return (
        db.query(DatabaseT4CModel)
        .filter(DatabaseT4CModel.id == id)
        .filter(DatabaseT4CModel.repository_name == repo_name)
        .first()
    )


def get_all_projects(db: Session, repo_name: str):
    return (
        db.query(DatabaseT4CModel)
        .filter(DatabaseT4CModel.repository_name == repo_name)
        .all()
    )


def create_project(db: Session, repo_name: str, project_name: str):
    project = DatabaseT4CModel(repository_name=repo_name, name=project_name)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, id: int, repo_name: str):
    db.query(DatabaseT4CModel).filter(DatabaseT4CModel.id == id).filter(
        DatabaseT4CModel.repository_name == repo_name
    ).delete()
    db.commit()
