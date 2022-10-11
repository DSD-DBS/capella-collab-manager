# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import typing as t

from fastapi import APIRouter, Depends, HTTPException
from requests import Session

from capellacollab.core.authentication.database import (
    check_git_settings_instance_exists,
    verify_admin,
)
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.authentication.responses import (
    AUTHENTICATION_RESPONSES,
)
from capellacollab.core.database import get_db
from capellacollab.projects.capellamodels.modelsources.git.models import (
    GetRevisionsModel,
    GitCredentials,
)
from capellacollab.settings.modelsources.git import crud
from capellacollab.settings.modelsources.git.core import get_remote_refs
from capellacollab.settings.modelsources.git.models import GitSettings

router = APIRouter()


@router.get("/", tags=["GitSettings"], responses=AUTHENTICATION_RESPONSES)
def list_git_settings(
    db: Session = Depends(get_db), token=Depends(JWTBearer())
):
    verify_admin(token, db)
    return crud.get_all_git_settings(db)


@router.get("/{id}", tags=["GitSettings"], responses=AUTHENTICATION_RESPONSES)
def get_git_settings(
    id: int, db: Session = Depends(get_db), token=Depends(JWTBearer())
):
    verify_admin(token, db)
    return crud.get_git_settings(db, id)


@router.post("/", tags=["GitSettings"], responses=AUTHENTICATION_RESPONSES)
def create_git_settings(
    body: GitSettings,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    verify_admin(token, db)
    return crud.create_git_settings(db, body)


@router.post("/revisions", response_model=GetRevisionsModel)
def get_revisions(
    url: str,
    credentials: GitCredentials,
    token: JWTBearer = Depends(JWTBearer()),
) -> GetRevisionsModel:
    username = credentials.username
    password = credentials.password

    return get_remote_refs(url, username, password)


@router.put("/{id}", tags=["GitSettings"], responses=AUTHENTICATION_RESPONSES)
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
    "/{id}", tags=["GitSettings"], responses=AUTHENTICATION_RESPONSES
)
def delete_git_settings(
    id: int, db: Session = Depends(get_db), token=Depends(JWTBearer())
):
    verify_admin(token, db)
    return crud.delete_git_settings(db, id)
