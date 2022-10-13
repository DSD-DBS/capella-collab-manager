# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import logging

import sqlalchemy.orm.session
from fastapi import APIRouter, Depends, HTTPException
from requests import Session

import capellacollab.projects.capellamodels.crud as capella_model_crud
import capellacollab.projects.crud as projects_crud
from capellacollab.core.authentication.database import verify_project_role
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.authentication.responses import (
    AUTHENTICATION_RESPONSES,
)
from capellacollab.core.database import get_db
from capellacollab.projects.capellamodels.modelsources.git.models import (
    NewGitSource,
    ResponseGitModel,
    ResponseGitSource,
)
from capellacollab.settings.modelsources.git.core import get_remote_refs
from capellacollab.settings.modelsources.git.crud import get_all_git_settings

from . import crud

router = APIRouter()
log = logging.getLogger(__name__)


def verify_path_prefix(path: str, db: sqlalchemy.orm.session.Session):
    git_settings = get_all_git_settings(db)

    if not git_settings:
        return

    for git_setting in git_settings:
        if path.startswith(git_setting.url):
            return

    raise HTTPException(
        status_code=400,
        detail={
            "err_code": "no_git_instance_with_prefix_found",
            "reason": "There exist no git instance with an url being a prefix of the provdided source path. Please check whether you correctly selected a git instance.",
        },
    )


def verify_valid_path_sequences(path: str):
    sequence_blacklist = ["..", "%"]

    invalid_sequences = []
    for sequence in sequence_blacklist:
        if sequence in path:
            invalid_sequences.append(sequence)

    if not invalid_sequences:
        return

    raise HTTPException(
        status_code=400,
        detail={
            "err_code": "invalid_path_sequences",
            "reason": "The provide source path contains invalid sequences.",
        },
    )


@router.post("/", response_model=ResponseGitSource)
def create_source(
    project_name: str,
    model_slug: str,
    source: NewGitSource,
    db: Session = Depends(get_db),
    token: JWTBearer = Depends(JWTBearer()),
):
    project_instance = projects_crud.get_project_by_name(db, project_name)
    verify_project_role(project_instance.name, token, db)

    verify_path_prefix(source.path, db)
    verify_valid_path_sequences(source.path)

    new_source = crud.create(db, project_instance.slug, model_slug, source)
    return ResponseGitSource.from_orm(new_source)


@router.get(
    "/primary/revisions",
    responses=AUTHENTICATION_RESPONSES,
)
def get_revisions_of_primary_git_model(
    project: str, db: Session = Depends(get_db), token=Depends(JWTBearer())
):
    git_model = crud.get_primary_gitmodel_of_capellamodels(db, project)
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


# FIXME: Add verification
@router.get("/git-models", response_model=list[ResponseGitModel])
def get_git_models(
    project_name: str,
    model_slug: str,
    db: Session = Depends(get_db),
    token: JWTBearer = Depends(JWTBearer()),
):
    project_instance = projects_crud.get_project_by_name(db, project_name)
    capella_model = capella_model_crud.get_model_by_slug(
        db, project_instance.slug, model_slug
    )
    git_models = crud.get_gitmodels_of_capellamodels(db, capella_model.id)

    response_git_models: list[ResponseGitSource] = [
        ResponseGitModel.from_orm(git_model) for git_model in git_models
    ]

    return response_git_models
