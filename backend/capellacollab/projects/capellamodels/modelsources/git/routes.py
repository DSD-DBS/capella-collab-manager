# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import capellacollab.projects.capellamodels.crud as capella_model_crud
import capellacollab.projects.crud as projects_crud
from capellacollab.core.authentication.database import verify_project_role
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.database import get_db
from capellacollab.projects.capellamodels.injectables import (
    get_existing_capella_model,
)
from capellacollab.projects.capellamodels.models import DatabaseCapellaModel
from capellacollab.projects.capellamodels.modelsources.git.models import (
    DB_GitModel,
    PatchGitModel,
    PostGitModel,
    ResponseGitModel,
)
from capellacollab.settings.modelsources.git.core import get_remote_refs
from capellacollab.settings.modelsources.git.crud import get_all_git_settings
from capellacollab.settings.modelsources.git.models import (
    GetRevisionsResponseModel,
)

from . import crud
from .injectables import get_existing_git_model, get_existing_primary_git_model

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


# FIXME: Add role verification: All roles?
@router.get("/git-models", response_model=list[ResponseGitModel])
def get_git_models(
    capella_model: DatabaseCapellaModel = Depends(get_existing_capella_model),
):
    return [
        ResponseGitModel.from_orm(git_model)
        for git_model in capella_model.git_models
    ]


# FIXME: Add role verification: Only manager and admin
@router.get("/git-model/{git_model_id}", response_model=ResponseGitModel)
def get_git_model_by_id(
    git_model: DB_GitModel = Depends(get_existing_git_model),
):
    return ResponseGitModel.from_orm(git_model)


# FIXME: Add role verification: All roles?
@router.get("/primary/revisions", response_model=GetRevisionsResponseModel)
def get_revisions_of_primary_git_model(
    capella_model: DatabaseCapellaModel = Depends(get_existing_capella_model),
    primary_git_model: DB_GitModel = Depends(get_existing_primary_git_model),
) -> GetRevisionsResponseModel:
    return get_remote_refs(
        primary_git_model.path,
        primary_git_model.username,
        primary_git_model.password,
        default=primary_git_model.revision,
    )


# FIXME: Add role verification: Only manager and admin
@router.post("/", response_model=ResponseGitModel)
def create_source(
    post_git_model: PostGitModel,
    capella_model: DatabaseCapellaModel = Depends(get_existing_capella_model),
    db: Session = Depends(get_db),
) -> ResponseGitModel:
    verify_path_prefix(db, post_git_model.path)

    new_git_model = crud.add_gitmodel_to_capellamodel(
        db, capella_model, post_git_model
    )
    return ResponseGitModel.from_orm(new_git_model)


# FIXME: Only manager and admin
@router.patch("/git-model/{git_model_id}", response_model=ResponseGitModel)
def update_git_model_by_id(
    patch_git_model: PatchGitModel,
    db_git_model: DB_GitModel = Depends(get_existing_git_model),
    db_capella_model: DatabaseCapellaModel = Depends(
        get_existing_capella_model
    ),
    db: Session = Depends(get_db),
) -> ResponseGitModel:
    verify_path_prefix(db, patch_git_model.path)

    updated_git_model = crud.update_git_model(
        db, db_capella_model, db_git_model, patch_git_model
    )

    return ResponseGitModel.from_orm(updated_git_model)
