# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

# Standard library:
import typing as t

# 3rd party:
from sqlalchemy.orm import Session

# 1st party:
from capellacollab.projects.models import DatabaseProject


def get_project(db: Session, name: str):
    return db.query(DatabaseProject).filter(DatabaseProject.name == name).first()


def get_all_projects(db: Session) -> t.List[DatabaseProject]:
    return db.query(DatabaseProject).all()


def create_project(db: Session, name: str) -> DatabaseProject:
    repo = DatabaseProject(name=name, users=[])
    db.add(repo)
    db.commit()
    db.refresh(repo)
    return repo


def delete_project(db: Session, name: str) -> None:
    db.query(DatabaseProject).filter(DatabaseProject.name == name).delete()
    db.commit()
