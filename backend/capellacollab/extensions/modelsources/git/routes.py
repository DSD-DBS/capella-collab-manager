# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import base64
import logging
import os
import typing as t

from fastapi import APIRouter, Depends, HTTPException
from requests import Session

import capellacollab.projects.crud as projects_crud
from capellacollab.core.authentication.database import verify_project_role
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.authentication.responses import (
    AUTHENTICATION_RESPONSES,
)
from capellacollab.core.database import get_db
from capellacollab.extensions.modelsources import git
from capellacollab.extensions.modelsources.git.crud import (
    get_primary_gitmodel_of_capellamodels,
)
from capellacollab.extensions.modelsources.git.models import (
    GetRepositoryGitModel,
    GetRevisionsModel,
    GitCredentials,
    NewGitSource,
    PatchRepositoryGitModel,
    PostGitModel,
    RepositoryGitInnerModel,
    ResponseGitModel,
    ResponseGitSource,
)

from . import crud
from .core import get_remote_refs, ls_remote

router = APIRouter()
log = logging.getLogger(__name__)


@router.post("/create/{model_slug}", response_model=ResponseGitSource)
def create_source(
    project: str,
    model_slug: str,
    source: NewGitSource,
    db: Session = Depends(get_db),
    token: JWTBearer = Depends(JWTBearer()),
):

    project_instance = projects_crud.get_project(db, project)
    verify_project_role(project_instance.name, token, db)
    new_source = crud.create(db, project_instance.slug, model_slug, source)
    return ResponseGitSource.from_orm(new_source)


@router.get(
    "/primary/revisions",
    responses=AUTHENTICATION_RESPONSES,
)
def get_revisions_of_primary_git_model(
    project: str, db: Session = Depends(get_db), token=Depends(JWTBearer())
):
    git_model = get_primary_gitmodel_of_capellamodels(db, project)
    if not git_model:
        raise HTTPException(
            status_code=500,
            detail={
                "err_code": "no_git_model",
                "reason": "No git model is assigned to your project. Please ask a project lead to assign a git model.",
            },
        )

    url = git_model.path
    username = git_model.username or ""
    password = git_model.password or ""

    log.debug(
        "Fetch revisions of git-model '%s' with url '%s'", git_model.name, url
    )

    remote_refs = get_remote_refs(url, username, password)
    remote_refs["default"] = git_model.revision

    log.debug("Determined default branch: %s", remote_refs["default"])

    return remote_refs


@router.post("/revisions", response_model=GetRevisionsModel)
def get_revisions(
    url: str,
    credentials: GitCredentials,
    token: JWTBearer = Depends(JWTBearer()),
) -> GetRevisionsModel:
    username = credentials.username
    password = credentials.password

    return get_remote_refs(url, username, password)
