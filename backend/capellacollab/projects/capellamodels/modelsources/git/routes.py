# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import logging

from fastapi import APIRouter, Depends, HTTPException
from requests import Session
from sqlalchemy.orm import Session

import capellacollab.projects.capellamodels.crud as capella_model_crud
import capellacollab.projects.crud as projects_crud
from capellacollab.core.authentication.database import verify_project_role
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.authentication.responses import (
    AUTHENTICATION_RESPONSES,
)
from capellacollab.core.database import get_db
from capellacollab.projects.capellamodels.modelsources.git.models import (
    PatchGitModel,
    PostGitModel,
    ResponseGitModel,
)
from capellacollab.settings.modelsources.git.core import get_remote_refs
from capellacollab.settings.modelsources.git.crud import get_all_git_settings

from . import crud

router = APIRouter()
log = logging.getLogger(__name__)


def verify_path_prefix(db: Session, path: str):
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


def verify_valid_git_model_on_project_and_capella_model(
    db: Session, project_slug: str, model_slug: str, git_model_id
):
    capella_model = capella_model_crud.get_model_by_slug(
        db, project_slug, model_slug
    )

    for git_model in capella_model.git_models:
        if git_model.id == git_model_id:
            return

    return HTTPException(
        status_code=400,
        detail={
            "err_code": "git_model_not_exists_on_project_and_model",
            "reason": "The git model does not exists on the capella model for the project",
        },
    )


@router.post("/", response_model=ResponseGitModel)
def create_source(
    project_slug: str,
    model_slug: str,
    source: PostGitModel,
    db: Session = Depends(get_db),
    token: JWTBearer = Depends(JWTBearer()),
):
    project_instance = projects_crud.get_project_by_slug(db, project_slug)
    verify_project_role(project_instance.name, token, db)

    verify_path_prefix(db, source.path)
    verify_valid_path_sequences(source.path)

    new_source = crud.add_gitmodel_to_capellamodel(
        db, project_instance.slug, model_slug, source
    )
    return ResponseGitModel.from_orm(new_source)


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


@router.get("/git-models", response_model=list[ResponseGitModel])
def get_git_models(
    project_slug: str,
    model_slug: str,
    db: Session = Depends(get_db),
    token: JWTBearer = Depends(JWTBearer()),
):
    project = projects_crud.get_project_by_slug(db, project_slug)
    verify_project_role(project, token, db)

    capella_model = capella_model_crud.get_model_by_slug(
        db, project.slug, model_slug
    )

    git_models = crud.get_gitmodels_of_capellamodels(db, capella_model.id)

    return git_models


@router.get("/git-model/{git_model_id}", response_model=ResponseGitModel)
def get_git_model_by_id(
    project_slug: str,
    model_slug: str,
    git_model_id: int,
    db: Session = Depends(get_db),
    token: JWTBearer = Depends(JWTBearer()),
):
    project = projects_crud.get_project_by_slug(db, project_slug)
    verify_project_role(project, token, db)

    verify_valid_git_model_on_project_and_capella_model(
        db, project_slug, model_slug, git_model_id
    )

    git_model = crud.get_gitmodel_by_id(db, git_model_id)
    if not git_model:
        raise HTTPException(
            status_code=500,
            detail={
                "err_code": "no_git_model",
                "reason": f"No git model with the id {git_model_id} exists",
            },
        )

    return git_model


@router.patch("/git-model/{git_model_id}", response_model=ResponseGitModel)
def update_git_model_by_id(
    project_slug: str,
    model_slug: str,
    git_model_id: int,
    git_model: PatchGitModel,
    db: Session = Depends(get_db),
    token: JWTBearer = Depends(JWTBearer()),
):
    project = projects_crud.get_project_by_slug(db, project_slug)
    verify_project_role(project, token, db)

    verify_valid_git_model_on_project_and_capella_model(
        db, project_slug, model_slug, git_model_id
    )

    verify_path_prefix(db, git_model.path)
    verify_valid_path_sequences(git_model.path)

    updated_git_model = crud.update_git_model(db, git_model_id, git_model)

    if git_model.primary and not updated_git_model.primary:
        capella_model = capella_model_crud.get_model_by_slug(
            db, project_slug, model_slug
        )
        updated_git_model = crud.make_git_model_primary(
            db, capella_model.id, git_model_id
        )

    return updated_git_model
