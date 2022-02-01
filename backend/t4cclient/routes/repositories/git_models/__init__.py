import typing as t

from fastapi import APIRouter, Depends
from requests import Session
from t4cclient.core.database import get_db, repository_git_models
from t4cclient.core.oauth.database import verify_repository_role
from t4cclient.core.oauth.database.git_models import verify_gitmodel_permission
from t4cclient.core.oauth.jwt_bearer import JWTBearer
from t4cclient.routes.open_api_configuration import AUTHENTICATION_RESPONSES
from t4cclient.schemas.repositories.git_models import (
    GetRepositoryGitModel,
    PatchRepositoryGitModel,
    RepositoryGitInnerModel,
    RepositoryGitModel,
)

from . import jenkins as router_jenkins

router = APIRouter()


@router.get(
    "/",
    response_model=t.List[GetRepositoryGitModel],
    responses=AUTHENTICATION_RESPONSES,
)
def get_models_for_repository(
    repository_name: str, db: Session = Depends(get_db), token=Depends(JWTBearer())
):
    verify_repository_role(repository_name, token=token, db=db)
    db_models = repository_git_models.get_models_of_repository(db, repository_name)
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
    repository_name: str,
    body: RepositoryGitModel,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    verify_repository_role(
        repository_name, allowed_roles=["manager", "administrator"], token=token, db=db
    )
    db_model = repository_git_models.add_model_to_repository(db, repository_name, body)
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

    return repository_git_models.delete_model_from_repository(
        db, repository_name, model_id
    )


@router.patch(
    "/{model_id}",
    response_model=GetRepositoryGitModel,
    responses=AUTHENTICATION_RESPONSES,
)
def patch_model(
    repository_name: str,
    body: PatchRepositoryGitModel,
    model_id: int,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    verify_repository_role(repository_name, token=token, db=db)
    verify_gitmodel_permission(repository_name, model_id, db)
    if body.primary is not None:
        db_model = repository_git_models.make_model_primary(
            db, repository_name, model_id
        )
        return GetRepositoryGitModel(
            **db_model.__dict__,
            model=RepositoryGitInnerModel(**db_model.__dict__),
        )
    return None


router.include_router(router_jenkins.router, prefix="/{model_id}/jenkins")
