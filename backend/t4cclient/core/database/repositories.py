# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

from sqlalchemy.orm import Session

from t4cclient.sql_models.repositories import DatabaseRepository


def get_repository(db: Session, name: str):
    return db.query(DatabaseRepository).filter(DatabaseRepository.name == name).first()


def get_all_repositories(db: Session) -> t.List[DatabaseRepository]:
    return db.query(DatabaseRepository).all()


def create_repository(db: Session, name: str):
    repo = DatabaseRepository(name=name, users=[])
    db.add(repo)
    db.commit()
    db.refresh(repo)
    return repo


def delete_repository(db: Session, name: str):
    db.query(DatabaseRepository).filter(DatabaseRepository.name == name).delete()
    db.commit()
