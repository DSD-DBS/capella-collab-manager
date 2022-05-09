# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

from sqlalchemy.orm import Session
from t4cclient.projects.models import DatabaseProject


def get_repository(db: Session, name: str):
    return db.query(DatabaseProject).filter(DatabaseProject.name == name).first()


def get_all_repositories(db: Session) -> t.List[DatabaseProject]:
    return db.query(DatabaseProject).all()


def create_repository(db: Session, name: str):
    repo = DatabaseProject(name=name, users=[])
    db.add(repo)
    db.commit()
    db.refresh(repo)
    return repo


def delete_repository(db: Session, name: str):
    db.query(DatabaseProject).filter(DatabaseProject.name == name).delete()
    db.commit()
