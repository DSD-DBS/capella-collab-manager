# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import Depends
from sqlalchemy.orm import Session

from capellacollab.core.database import get_db
from capellacollab.projects.capellamodels.backups.models import DatabaseBackup

from . import crud


def get_backup_settings(
    db: Session = Depends(get_db),
) -> DatabaseBackup:
    return crud.get_backup_settings(db)
