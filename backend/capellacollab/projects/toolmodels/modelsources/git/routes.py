# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import logging

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from capellacollab.core.authentication.database import ProjectRoleVerification
from capellacollab.core.database import get_db
from capellacollab.projects.toolmodels.injectables import (
    get_existing_capella_model,
)
from capellacollab.projects.toolmodels.models import DatabaseCapellaModel
from capellacollab.projects.toolmodels.modelsources.git.models import (
    DatabaseGitModel,
    PatchGitModel,
    PostGitModel,
    ResponseGitModel,
)
from capellacollab.projects.users.models import ProjectUserRole
from capellacollab.settings.modelsources.git.core import get_remote_refs
from capellacollab.settings.modelsources.git.crud import get_git_settings
from capellacollab.settings.modelsources.git.models import (
    GetRevisionsResponseModel,
)

from . import crud
from .injectables import get_existing_git_model, get_existing_primary_git_model

router = APIRouter()
log = logging.getLogger(__name__)


def verify_path_prefix(db: Session, path: str):
    git_settings = get_git_settings(db)

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


@router.get("", response_model=list[ResponseGitModel])
def get_git_models(
    capella_model: DatabaseCapellaModel = Depends(get_existing_capella_model),
) -> list[DatabaseGitModel]:
    return capella_model.git_models


@router.get(
    "/{git_model_id}",
    response_model=ResponseGitModel,
    dependencies=[
        Depends(ProjectRoleVerification(required_role=ProjectUserRole.MANAGER))
    ],
)
def get_git_model_by_id(
    git_model: DatabaseGitModel = Depends(get_existing_git_model),
) -> DatabaseGitModel:
    return git_model


@router.get("/primary/revisions", response_model=GetRevisionsResponseModel)
def get_revisions_of_primary_git_model(
    primary_git_model: DatabaseGitModel = Depends(
        get_existing_primary_git_model
    ),
) -> GetRevisionsResponseModel:
    return get_remote_refs(
        primary_git_model.path,
        primary_git_model.username,
        primary_git_model.password,
        default=primary_git_model.revision,
    )


@router.post(
    "/{git_model_id}/revisions",
    response_model=GetRevisionsResponseModel,
    dependencies=[
        Depends(ProjectRoleVerification(required_role=ProjectUserRole.MANAGER))
    ],
)
def get_revisions_with_model_credentials(
    url: str = Body(),
    git_model: DatabaseGitModel = Depends(get_existing_git_model),
):
    return get_remote_refs(url, git_model.username, git_model.password)


@router.post(
    "",
    response_model=ResponseGitModel,
    dependencies=[
        Depends(ProjectRoleVerification(required_role=ProjectUserRole.MANAGER))
    ],
)
def create_git_model(
    post_git_model: PostGitModel,
    capella_model: DatabaseCapellaModel = Depends(get_existing_capella_model),
    db: Session = Depends(get_db),
) -> DatabaseGitModel:
    verify_path_prefix(db, post_git_model.path)

    new_git_model = crud.add_gitmodel_to_capellamodel(
        db, capella_model, post_git_model
    )
    return new_git_model


@router.put(
    "/{git_model_id}",
    response_model=ResponseGitModel,
    dependencies=[
        Depends(ProjectRoleVerification(required_role=ProjectUserRole.MANAGER))
    ],
)
def update_git_model_by_id(
    patch_git_model: PatchGitModel,
    db_git_model: DatabaseGitModel = Depends(get_existing_git_model),
    db_capella_model: DatabaseCapellaModel = Depends(
        get_existing_capella_model
    ),
    db: Session = Depends(get_db),
) -> DatabaseGitModel:
    verify_path_prefix(db, patch_git_model.path)

    updated_git_model = crud.update_git_model(
        db, db_capella_model, db_git_model, patch_git_model
    )

    return updated_git_model
