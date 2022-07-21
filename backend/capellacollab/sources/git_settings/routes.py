# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

# Standard library:
import typing as t

# 3rd party:
from fastapi import APIRouter, Depends, HTTPException
from requests import Session

# 1st party:
from capellacollab.core.authentication.database import verify_project_role, is_admin
from capellacollab.core.authentication.database.git_models import (
    verify_gitmodel_permission,
)
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.database import get_db
from capellacollab.sources.git_settings import crud
from capellacollab.sources.git_settings.models import (
    GitSettings,
    GitSettingsGitGetResponse,
    GitType,
)
from capellacollab.routes.open_api_configuration import AUTHENTICATION_RESPONSES

router = APIRouter()


@router.get("/", tags=["Git-Settings"], responses=AUTHENTICATION_RESPONSES)
def list_git_settings(db: Session = Depends(get_db), token=Depends(JWTBearer())):
    if is_admin(token, db):
        return crud.get_all_git_settings(db)

    # TODO: can manager get git settings? how to associate user with git settings?

    raise HTTPException(
        status_code=500,
        detail="The role administrator is required for this transaction.",
    )


@router.get("/{id}", tags=["Git-Settings"], responses=AUTHENTICATION_RESPONSES)
def get_git_settings(
    id: int, db: Session = Depends(get_db), token=Depends(JWTBearer())
):
    if is_admin(token, db):
        return crud.get_git_settings(db, id)

    raise HTTPException(
        status_code=500,
        detail="The role administrator is required for this transaction.",
    )


@router.post("/", tags=["Git-Settings"], responses=AUTHENTICATION_RESPONSES)
def create_git_settings(
    body: GitSettings, db: Session = Depends(get_db), token=Depends(JWTBearer())
):
    if is_admin(token, db):
        return crud.create_git_settings(db, body)

    raise HTTPException(
        status_code=500,
        detail="The role administrator is required for this transaction.",
    )


@router.put("/{id}", tags=["Git-Settings"], responses=AUTHENTICATION_RESPONSES)
def edit_git_settings(id: int, body: GitSettings):
    pass


@router.delete("/{id}", tags=["Git-Settings"], responses=AUTHENTICATION_RESPONSES)
def delete_git_settings(
    id: int, db: Session = Depends(get_db), token=Depends(JWTBearer())
):
    if is_admin(token, db):
        return crud.delete_git_settings(db, id)

    raise HTTPException(
        status_code=500,
        detail="The role administrator is required for this transaction.",
    )
