# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import typing as t

import sqlalchemy.orm.session
from fastapi import APIRouter, Depends, HTTPException
from requests import Session

from capellacollab.core.authentication.database import verify_admin
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.authentication.responses import (
    AUTHENTICATION_RESPONSES,
)
from capellacollab.core.database import get_db
from capellacollab.settings.modelsources.git import crud
from capellacollab.settings.modelsources.git.models import GitSettings

router = APIRouter()


def check_git_settings_instance_exists(
    db: sqlalchemy.orm.session.Session,
    id: int,
):
    instance = crud.get_git_settings(db, id)
    if not instance:
        raise HTTPException(
            status_code=404,
            detail={
                "reason": f"The git instance with id {id} does not exist."
            },
        )


@router.get("/", tags=["Git-Settings"], responses=AUTHENTICATION_RESPONSES)
def list_git_settings(
    db: Session = Depends(get_db), token=Depends(JWTBearer())
):
    verify_admin(token, db)
    return crud.get_all_git_settings(db)


@router.get("/{id}", tags=["Git-Settings"], responses=AUTHENTICATION_RESPONSES)
def get_git_settings(
    id: int, db: Session = Depends(get_db), token=Depends(JWTBearer())
):
    verify_admin(token, db)
    return crud.get_git_settings(db, id)


@router.post("/", tags=["Git-Settings"], responses=AUTHENTICATION_RESPONSES)
def create_git_settings(
    body: GitSettings,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    verify_admin(token, db)
    return crud.create_git_settings(db, body)


@router.put("/{id}", tags=["Git-Settings"], responses=AUTHENTICATION_RESPONSES)
def edit_git_settings(
    id: int,
    body: GitSettings,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    verify_admin(token, db)
    check_git_settings_instance_exists(db, id)
    return crud.update_git_settings(db, id, body)


@router.delete(
    "/{id}", tags=["Git-Settings"], responses=AUTHENTICATION_RESPONSES
)
def delete_git_settings(
    id: int, db: Session = Depends(get_db), token=Depends(JWTBearer())
):
    verify_admin(token, db)
    return crud.delete_git_settings(db, id)
