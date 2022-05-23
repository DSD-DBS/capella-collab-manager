# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

# Standard library:
import base64
import typing as t

# 3rd party:
from fastapi import APIRouter, Depends
from requests import Session

# 1st party:
from capellacollab.core.authentication.database import verify_repository_role
from capellacollab.core.authentication.database.git_models import (
    verify_gitmodel_permission,
)
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.database import get_db
from capellacollab.extensions.modelsources import git
from capellacollab.extensions.modelsources.git.models import (
    GetRepositoryGitModel,
    PatchRepositoryGitModel,
    PostGitModel,
    RepositoryGitInnerModel,
    RepositoryGitModel,
)
from capellacollab.routes.open_api_configuration import AUTHENTICATION_RESPONSES

router = APIRouter()


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
