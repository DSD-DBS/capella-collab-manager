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


def stage_repository_for_deletion(db: Session, project_name: str, username: str):
    repo = get_repository(db, project_name)
    repo.staged_by = username
    db.commit()
    db.refresh(repo)
    return repo


def stage_status(db: Session, project_name: str):
    repo = get_repository(db, project_name)
    if repo.staged_by is not None and repo.staged_by != "":
        return True
    return False
