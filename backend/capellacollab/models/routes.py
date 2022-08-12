# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

# Standard library:
import typing as t

# 3rd party:
from fastapi import APIRouter, Depends, HTTPException
from requests import Session

# local:
from . import crud
from .models import EmptyModel, NewModel, ResponseModel, ToolDetails

# 1st party:
from capellacollab.core.authentication.database import verify_project_role
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.database import get_db
from capellacollab.projects import crud as projects_crud

router = APIRouter()


@router.get("/{project_slug}/", response_model=t.List[ResponseModel])
def get_id(
    project_slug: str, db: Session = Depends(get_db), token=Depends(JWTBearer())
) -> t.List[ResponseModel]:

    project = projects_crud.get_slug(db, project_slug)
    if not project:
        raise HTTPException(404, "Project not found.")

    return [ResponseModel.from_model(model) for model in crud.get_all(db, project.slug)]


@router.get("/{project_slug}/details/", response_model=ResponseModel)
def get_slug(
    project_slug: str,
    slug: str,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
) -> ResponseModel:

    project = projects_crud.get_slug(db, project_slug)
    if not project:
        raise HTTPException(404, "Project not found.")
    response_model = ResponseModel.from_model(crud.get_slug(db, project_slug, slug))
    return response_model


@router.post("/{project_slug}/create-empty/", response_model=ResponseModel)
def create_empty(
    project_slug: str,
    new_model: EmptyModel,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
) -> ResponseModel:

    project = projects_crud.get_slug(db, project_slug)
    verify_project_role(
        repository=project.name,
        token=token,
        db=db,
        allowed_roles=["manager", "administrator"],
    )

    return ResponseModel.from_model(crud.create_empty(db, project_slug, new_model))


@router.post("/{project_slug}/create-new/", response_model=ResponseModel)
def create_new(
    project_slug: str,
    new_model: NewModel,
    db: Session = Depends(get_db),
    token: JWTBearer = Depends(JWTBearer()),
) -> ResponseModel:

    project = projects_crud.get_slug(db, project_slug)
    verify_project_role(
        repository=project.name,
        token=token,
        db=db,
        allowed_roles=["manager", "administrator"],
    )

    return ResponseModel.from_model(crud.create_new(db, project_slug, new_model))


@router.patch(
    "/{project_slug}/set-tool-details/{model_slug}/", response_model=ResponseModel
)
def set_tool_details(
    project_slug: str,
    model_slug: str,
    tool_details: ToolDetails,
    db: Session = Depends(get_db),
    token: JWTBearer = Depends(JWTBearer()),
):

    project = projects_crud.get_slug(db, project_slug)
    if not project:
        raise HTTPException(404, "Project Not found.")
    verify_project_role(project.name, token, db, ["manager", "administrator"])
    model = crud.get_slug(db, project.slug, model_slug)
    if not model:
        raise HTTPException(404, "Model not found.")

    return ResponseModel.from_model(
        crud.set_tool_details(
            db,
            model,
            tool_details,
        )
    )


@router.post("/{project_slug}/create-git/", response_model=ResponseModel)
def create_git(
    project_slug: str,
    new_model: EmptyModel,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):

    pass
