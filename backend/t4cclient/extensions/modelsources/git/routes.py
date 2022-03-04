import base64
import typing as t

from fastapi import APIRouter, Depends
from requests import Session
from t4cclient.core.database import get_db
from t4cclient.core.oauth.database import verify_repository_role
from t4cclient.core.oauth.database.git_models import verify_gitmodel_permission
from t4cclient.core.oauth.jwt_bearer import JWTBearer
from t4cclient.extensions.modelsources import git
from t4cclient.extensions.modelsources.git.models import (
    GetRepositoryGitModel,
    PatchRepositoryGitModel,
    RepositoryGitInnerModel,
    RepositoryGitModel,
)
from t4cclient.routes.open_api_configuration import AUTHENTICATION_RESPONSES

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
    body: RepositoryGitModel,
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
    repository_name: str,
    model_id: int,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    verify_repository_role(
        repository_name, allowed_roles=["manager", "administrator"], token=token, db=db
    )
    verify_gitmodel_permission(repository_name, model_id, db)
    return git.crud.delete_model_from_repository(db, repository_name, model_id)


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
