# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

from sqlalchemy.orm import Session

from . import models


def get_backup(db: Session, project: str, id: int):
    return (
        db.query(models.DB_EASEBackup)
        .filter(models.DB_EASEBackup.id == id)
        .filter(models.DB_EASEBackup.project == project)
        .first()
    )


def get_backups(db: Session, project: str) -> t.List[models.DB_EASEBackup]:
    return (
        db.query(models.DB_EASEBackup)
        .filter(models.DB_EASEBackup.project == project)
        .all()
    )


def create_backup(db: Session, backup: models.DB_EASEBackup):
    db.add(backup)
    db.commit()
    db.refresh(backup)
    return backup


def delete_backup(db: Session, project: str, id: int):
    db.query(models.DB_EASEBackup).filter(
        models.DB_EASEBackup.id == id
    ).filter(models.DB_EASEBackup.project == project).delete()
    db.commit()
