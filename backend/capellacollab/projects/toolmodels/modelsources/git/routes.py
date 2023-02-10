# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import urllib.parse

from fastapi import APIRouter, Body, Depends, HTTPException
from requests import Request
from sqlalchemy.orm import Session

from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.core.database import get_db
from capellacollab.projects.toolmodels.backups.crud import (
    get_pipelines_for_git_model,
)
from capellacollab.projects.toolmodels.injectables import (
    get_existing_capella_model,
)
from capellacollab.projects.toolmodels.models import DatabaseCapellaModel
from capellacollab.projects.toolmodels.modelsources.git.models import (
    DatabaseGitModel,
    GitModel,
    PatchGitModel,
    PostGitModel,
)
from capellacollab.projects.users.models import ProjectUserRole
from capellacollab.settings.modelsources.git.core import get_remote_refs
from capellacollab.settings.modelsources.git.crud import get_git_instances
from capellacollab.settings.modelsources.git.models import (
    GetRevisionsResponseModel,
)

from . import crud
from .injectables import get_existing_git_model, get_existing_primary_git_model

router = APIRouter()
log = logging.getLogger(__name__)


def verify_path_prefix(db: Session, path: str):
    if not (git_instances := get_git_instances(db)):
        return

    unquoted_path = urllib.parse.unquote(path)
    if resolved_path := Request("GET", unquoted_path).prepare().url:
        for git_instance in git_instances:
            unquoted_git_url = urllib.parse.unquote(git_instance.url)
            resolved_git_url = Request("GET", unquoted_git_url).prepare().url

            if resolved_git_url and resolved_path.startswith(resolved_git_url):
                return

    raise HTTPException(
        status_code=400,
        detail={
            "err_code": "no_git_instance_with_prefix_found",
            "reason": "There exist no git instance having the resolved path as prefix. Please check whether you correctly selected a git instance.",
        },
    )


@router.post("/validate/path", response_model=bool)
def validate_path(url: str = Body(), db: Session = Depends(get_db)) -> bool:
    try:
        verify_path_prefix(db, url)
        return True
    except Exception:
        return False


@router.get("", response_model=list[GitModel])
def get_git_models(
    capella_model: DatabaseCapellaModel = Depends(get_existing_capella_model),
) -> list[DatabaseGitModel]:
    return capella_model.git_models


@router.get(
    "/{git_model_id}",
    response_model=GitModel,
    dependencies=[
        Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=ProjectUserRole.MANAGER
            )
        )
    ],
)
def get_git_model_by_id(
    git_model: DatabaseGitModel = Depends(get_existing_git_model),
) -> DatabaseGitModel:
    return git_model


@router.get(
    "/primary/revisions",
    response_model=GetRevisionsResponseModel,
    dependencies=[
        Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=ProjectUserRole.MANAGER
            )
        )
    ],
)
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
        Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=ProjectUserRole.USER
            )
        )
    ],
)
def get_revisions_with_model_credentials(
    url: str = Body(),
    git_model: DatabaseGitModel = Depends(get_existing_git_model),
):
    return get_remote_refs(url, git_model.username, git_model.password)


@router.post(
    "",
    response_model=GitModel,
    dependencies=[
        Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=ProjectUserRole.MANAGER
            )
        )
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
    response_model=GitModel,
    dependencies=[
        Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=ProjectUserRole.MANAGER
            )
        )
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


@router.delete(
    "/{git_model_id}",
    status_code=204,
    dependencies=[
        Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=ProjectUserRole.MANAGER
            )
        )
    ],
)
def delete_git_model_by_id(
    db_git_model: DatabaseGitModel = Depends(get_existing_git_model),
    db: Session = Depends(get_db),
):
    if get_pipelines_for_git_model(db, db_git_model):
        raise HTTPException(
            status_code=409,
            detail={
                "err_code": "git_model_used_for_backup",
                "reason": "The git model can't be deleted: it's used for backup jobs",
            },
        )

    crud.delete_git_model(db, db_git_model)
