# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import typing as t

from sqlalchemy.orm import Session

from capellacollab.extensions.backups.ease.models import DB_EASEBackup


# FIXME: Remove usages of project name here (must be first changed in DB_EASEBackup)
def get_backup(db: Session, project_name: str, backup_id: int):
    return (
        db.query(DB_EASEBackup)
        .filter(DB_EASEBackup.id == backup_id)
        .filter(DB_EASEBackup.project == project_name)
        .first()
    )


# FIXME: Remove usages of project name here (must be first changed in DB_EASEBackup)
def get_backups(db: Session, project_name: str) -> t.List[DB_EASEBackup]:
    return (
        db.query(DB_EASEBackup)
        .filter(DB_EASEBackup.project == project_name)
        .all()
    )


def create_backup(db: Session, backup: DB_EASEBackup):
    db.add(backup)
    db.commit()
    return backup


# FIXME: Remove usages of project name here (must be first changed in DB_EASEBackup)
def delete_backup(db: Session, project_name: str, backup_id: int):
    db.query(DB_EASEBackup).filter(DB_EASEBackup.id == backup_id).filter(
        DB_EASEBackup.project == project_name
    ).delete()
    db.commit()
