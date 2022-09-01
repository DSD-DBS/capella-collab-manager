# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from sqlalchemy.orm import Session

from t4cclient.extensions.modelsources.t4c.models import DatabaseProject


def get_project(db: Session, name: str, repo_name: str):
    return (
        db.query(DatabaseProject)
        .filter(DatabaseProject.name == name)
        .filter(DatabaseProject.repository_name == repo_name)
        .first()
    )


def get_project_by_id(db: Session, id: int, repo_name: str):
    return (
        db.query(DatabaseProject)
        .filter(DatabaseProject.id == id)
        .filter(DatabaseProject.repository_name == repo_name)
        .first()
    )


def get_all_projects(db: Session, repo_name: str):
    return (
        db.query(DatabaseProject)
        .filter(DatabaseProject.repository_name == repo_name)
        .all()
    )


def create_project(db: Session, repo_name: str, project_name: str):
    project = DatabaseProject(repository_name=repo_name, name=project_name)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, id: int, repo_name: str):
    db.query(DatabaseProject).filter(DatabaseProject.id == id).filter(
        DatabaseProject.repository_name == repo_name
    ).delete()
    db.commit()
