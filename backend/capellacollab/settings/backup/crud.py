# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import BackupSettings, DatabaseBackupSettings


def get_backup_settings(db: Session) -> BackupSettings:
    return db.execute(select(DatabaseBackupSettings)).scalar_one()


def update_backup_settings(
    db: Session, backup: DatabaseBackupSettings, docker_image: str
) -> DatabaseBackupSettings:
    backup.docker_image = docker_image
    db.commit()
    return backup
