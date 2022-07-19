import typing as t
from fastapi import APIRouter, Depends
from requests import Session

from capellacollab.core.authentication.database import verify_project_role
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.database import get_db
from capellacollab.projects import crud as projects_crud

from . import crud
from .models import DB_CapellaModel, NewModel, ResponseModel


router = APIRouter()


@router.get('/{project_slug}/', response_model=t.List[ResponseModel])
def list_models(project_slug: str, db: Session = Depends(get_db),
    token = Depends(JWTBearer())):
    project = projects_crud.get_slug(db, project_slug)
    verify_project_role(project.name, token, db)
    return [ResponseModel.from_model(model) for model in crud.get_all(db, project_slug)]


@router.get('/{project_slug}/details/')
def get_slug(project_slug: str, id: t.Optional[int],
    db: Session = Depends(get_db), token = Depends(JWTBearer())):
    project = projects_crud.get_slug(db, project_slug)
    verify_project_role(project, token, db)
    return ResponseModel.from_model(crud.get_slug(db, project_slug, id))


@router.post('/{project_slug}/create-empty', response_model=ResponseModel)
def create_empty(project_slug, model: NewModel, db: Session = Depends(get_db),
    token=Depends(JWTBearer())) -> ResponseModel:
    project = projects_crud.get_slug(db, project_slug)
    verify_project_role(repository=project.name, token=token, db=db,
        allowed_roles=["manager", "administrator"])
    response_model = ResponseModel.from_model(crud.create(db, project_slug, model))
    return response_model

