# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import base64
import logging
import os
import typing as t

from fastapi import APIRouter, Depends, HTTPException
from requests import Session

from t4cclient.core.authentication.database import verify_repository_role
from t4cclient.core.authentication.database.git_models import (
    verify_gitmodel_permission,
)
from t4cclient.core.authentication.jwt_bearer import JWTBearer
from t4cclient.core.database import get_db
from t4cclient.core.oauth.responses import AUTHENTICATION_RESPONSES
from t4cclient.extensions.modelsources import git
from t4cclient.extensions.modelsources.git.crud import (
    get_primary_model_of_repository,
)
from t4cclient.extensions.modelsources.git.models import (
    GetRepositoryGitModel,
    PatchRepositoryGitModel,
    PostGitModel,
    RepositoryGitInnerModel,
)

from .core import ls_remote

router = APIRouter()
log = logging.getLogger(__name__)


@router.get(
    "/",
    response_model=t.List[GetRepositoryGitModel],
    responses=AUTHENTICATION_RESPONSES,
)
def get_models_for_repository(
    project: str, db: Session = Depends(get_db), token=Depends(JWTBearer())
):
    verify_repository_role(project, token=token, db=db)
    db_models = git.crud.get_models_of_repository(db, project)
    return_models: t.List[GetRepositoryGitModel] = []
    for db_model in db_models:
        return_models.append(
            GetRepositoryGitModel(
                **db_model.__dict__,
                model=RepositoryGitInnerModel(**db_model.__dict__),
            )
        )
    return return_models


@router.post(
    "/", response_model=GetRepositoryGitModel, responses=AUTHENTICATION_RESPONSES
)
def assign_model_to_repository(
    project: str,
    body: PostGitModel,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    verify_repository_role(
        project, allowed_roles=["manager", "administrator"], token=token, db=db
    )
    body.model.path = base64.b64decode(body.model.path).decode("utf-8")
    db_model = git.crud.add_model_to_repository(db, project, body)
    return GetRepositoryGitModel(
        **db_model.__dict__,
        model=RepositoryGitInnerModel(**db_model.__dict__),
    )


@router.delete(
    "/{model_id}",
    status_code=204,
    responses=AUTHENTICATION_RESPONSES,
)
def unassign_model_from_repository(
    project: str,
    model_id: int,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    verify_repository_role(
        project, allowed_roles=["manager", "administrator"], token=token, db=db
    )
    verify_gitmodel_permission(project, model_id, db)
    git.crud.delete_model_from_repository(db, project, model_id)
    return None


@router.patch(
    "/{model_id}",
    response_model=GetRepositoryGitModel,
    responses=AUTHENTICATION_RESPONSES,
)
def patch_model(
    project: str,
    body: PatchRepositoryGitModel,
    model_id: int,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    verify_repository_role(project, token=token, db=db)
    verify_gitmodel_permission(project, model_id, db)
    if body.primary is not None:
        db_model = git.crud.make_model_primary(db, project, model_id)
        return GetRepositoryGitModel(
            **db_model.__dict__,
            model=RepositoryGitInnerModel(**db_model.__dict__),
        )
    return None


@router.get(
    "/primary/revisions", tags=["Repositories"], responses=AUTHENTICATION_RESPONSES
)
def get_revisions(
    project: str, db: Session = Depends(get_db), token=Depends(JWTBearer())
):
    remote_refs: dict[str, list[str]] = {"branches": [], "tags": []}

    git_model = get_primary_model_of_repository(db, project)
    if not git_model:
        raise HTTPException(
            status_code=500,
            detail={
                "err_code": "no_git_model",
                "reason": "No git model is assigned to your project. Please ask a project lead to assign a git model.",
            },
        )

    url = git_model.path
    log.debug("Fetch revisions of git-model '%s' with url '%s'", git_model.name, url)

    git_env = os.environ.copy()
    git_env["GIT_USERNAME"] = git_model.username or ""
    git_env["GIT_PASSWORD"] = git_model.password or ""
    for ref in ls_remote(url, git_env):
        (_, ref) = ref.split("\t")
        if "^" in ref:
            continue
        if ref.startswith("refs/heads/"):
            remote_refs["branches"].append(ref[len("refs/heads/") :])
        elif ref.startswith("refs/tags/"):
            remote_refs["tags"].append(ref[len("refs/tags/") :])

    remote_refs["default"] = git_model.revision

    log.debug("Determined branches: %s", remote_refs["branches"])
    log.debug("Determined tags: %s", remote_refs["tags"])
    log.debug("Determined default branch: %s", remote_refs["default"])
    return remote_refs
