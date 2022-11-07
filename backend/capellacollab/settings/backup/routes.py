# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import logging
import typing as t

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from capellacollab.core.authentication.database import RoleVerification
from capellacollab.core.database import get_db
from capellacollab.users.models import Role

router = APIRouter()
log = logging.getLogger(__name__)

from . import crud, injectables
from .models import BackupSettings


@router.get(
    "",
    response_model=BackupSettings,
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
)
def get_backup_settings(
    backup: BackupSettings = Depends(injectables.get_backup_settings),
):
    return backup


@router.put(
    "",
    response_model=BackupSettings,
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
)
def set_backup_settings(
    body: BackupSettings,
    backup: BackupSettings = Depends(injectables.get_backup_settings),
    db: Session = Depends(get_db),
):
    return crud.update_backup_settings(db, backup, body.docker_image)
