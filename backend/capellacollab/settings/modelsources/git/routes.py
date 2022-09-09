# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


# Standard library:
import typing as t

# 3rd party:
from fastapi import APIRouter, Depends, HTTPException
from requests import Session

# 1st party:
from capellacollab.core.authentication.database import (
    check_git_settings_instance_exists,
    is_admin,
)
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.authentication.responses import (
    AUTHENTICATION_RESPONSES,
)
from capellacollab.core.database import get_db
from capellacollab.settings.modelsources.git import crud
from capellacollab.settings.modelsources.git.models import GitSettings

router = APIRouter()


@router.get("/", tags=["Git-Settings"], responses=AUTHENTICATION_RESPONSES)
def list_git_settings(
    db: Session = Depends(get_db), token=Depends(JWTBearer())
):
    if is_admin(token, db):
        return crud.get_all_git_settings(db)

    raise HTTPException(
        status_code=403,
        detail="The role administrator is required for this transaction.",
    )


@router.get("/{id}", tags=["Git-Settings"], responses=AUTHENTICATION_RESPONSES)
def get_git_settings(
    id: int, db: Session = Depends(get_db), token=Depends(JWTBearer())
):
    if is_admin(token, db):
        return crud.get_git_settings(db, id)

    raise HTTPException(
        status_code=403,
        detail="The role administrator is required for this transaction.",
    )


@router.post("/", tags=["Git-Settings"], responses=AUTHENTICATION_RESPONSES)
def create_git_settings(
    body: GitSettings,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    if is_admin(token, db):
        return crud.create_git_settings(db, body)

    raise HTTPException(
        status_code=403,
        detail="The role administrator is required for this transaction.",
    )


@router.put("/{id}", tags=["Git-Settings"], responses=AUTHENTICATION_RESPONSES)
def edit_git_settings(
    id: int,
    body: GitSettings,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    check_git_settings_instance_exists(db, id)
    if is_admin(token, db):
        return crud.update_git_settings(db, id, body)

    raise HTTPException(
        status_code=403,
        detail="The role administrator is required for this transaction.",
    )


@router.delete(
    "/{id}", tags=["Git-Settings"], responses=AUTHENTICATION_RESPONSES
)
def delete_git_settings(
    id: int, db: Session = Depends(get_db), token=Depends(JWTBearer())
):
    if is_admin(token, db):
        return crud.delete_git_settings(db, id)

    raise HTTPException(
        status_code=403,
        detail="The role administrator is required for this transaction.",
    )
