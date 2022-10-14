# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import typing as t

import sqlalchemy.orm.session
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from capellacollab.core.authentication.database import verify_admin
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.database import get_db
from capellacollab.settings.modelsources.git import crud
from capellacollab.settings.modelsources.git.core import get_remote_refs
from capellacollab.settings.modelsources.git.models import (
    GetRevisionModel,
    GetRevisionsResponseModel,
    GitSettings,
)

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


@router.get("/")
def list_git_settings(
    db: Session = Depends(get_db), token=Depends(JWTBearer())
):
    verify_admin(token, db)
    return crud.get_all_git_settings(db)


@router.get("/{id}")
def get_git_settings(
    id: int, db: Session = Depends(get_db), token=Depends(JWTBearer())
):
    verify_admin(token, db)
    return crud.get_git_settings(db, id)


@router.post("/")
def create_git_settings(
    body: GitSettings,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    verify_admin(token, db)
    return crud.create_git_settings(db, body)


# In the future, check if the HTTP QUERY method is available in fast api,
# and if so, use it instead of POST
# (https://www.ietf.org/archive/id/draft-ietf-httpbis-safe-method-w-body-02.html)
@router.post("/revisions", response_model=GetRevisionsResponseModel)
def get_revisions(
    body: GetRevisionModel,
) -> GetRevisionsResponseModel:
    url = body.url
    username = body.credentials.username
    password = body.credentials.password

    return get_remote_refs(url, username, password)


@router.put("/{id}")
def edit_git_settings(
    id: int,
    body: GitSettings,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    verify_admin(token, db)
    check_git_settings_instance_exists(db, id)
    return crud.update_git_settings(db, id, body)


@router.delete("/{id}")
def delete_git_settings(
    id: int, db: Session = Depends(get_db), token=Depends(JWTBearer())
):
    verify_admin(token, db)
    return crud.delete_git_settings(db, id)
