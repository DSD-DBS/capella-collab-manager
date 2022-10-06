# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import typing as t

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import Session

from capellacollab.core.authentication.database import verify_project_role
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.database import get_db
from capellacollab.projects import crud as projects_crud
from capellacollab.tools import crud as tools_crud

from . import crud
from .models import CapellaModel, ResponseModel, ToolDetails

router = APIRouter()


@router.get("/", response_model=t.List[ResponseModel])
def list_in_project(
    project_slug: str,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
) -> t.List[ResponseModel]:

    project = projects_crud.get_project_by_slug(db, project_slug)
    if not project:
        raise HTTPException(
            404,
            {
                "reason": f"The project having the name {project_slug} was not found.",
                "technical": f"No project with {project_slug} found.",
            },
        )
    verify_project_role(project.name, token, db)
    return [
        ResponseModel.from_orm(model)
        for model in crud.get_all_models_in_project(db, project.slug)
    ]


@router.get("/{slug}", response_model=ResponseModel)
def get_model_by_slug(
    project_slug: str,
    slug: str,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
) -> ResponseModel:

    project = projects_crud.get_project_by_slug(db, project_slug)
    if not project:
        raise HTTPException(
            404,
            {
                "reason": f"The project having the name {project_slug} was not found.",
                "technical": f"No project with {project_slug} found.",
            },
        )
    verify_project_role(project.name, token, db)
    model = crud.get_model_by_slug(db, project_slug, slug)
    if not model:
        raise HTTPException(
            404,
            {
                "reason": f"The model having the name {slug} of the project {project.name} was not found.",
                "technical": f"No model with {slug} found in the project {project.name}.",
            },
        )

    return ResponseModel.from_orm(model)


@router.post("/", response_model=ResponseModel)
def create_new(
    project_slug: str,
    new_model: CapellaModel,
    db: Session = Depends(get_db),
    token: JWTBearer = Depends(JWTBearer()),
) -> ResponseModel:

    project = projects_crud.get_project_by_slug(db, project_slug)
    if not project:
        raise HTTPException(
            404,
            {
                "reason": f"The project having the name {project_slug} was not found.",
                "technical": f"No project with {project_slug} found.",
            },
        )
    verify_project_role(
        repository=project.name,
        token=token,
        db=db,
        allowed_roles=["manager", "administrator"],
    )
    try:
        tool = tools_crud.get_tool_by_id(new_model.tool_id, db)
    except IntegrityError:
        raise HTTPException(
            404,
            {"reason": f"The tool with id {new_model.tool_id} was not found."},
        )
    try:
        model = crud.create_new_model(db, project, new_model, tool)
    except IntegrityError:
        raise HTTPException(
            409,
            {
                "reason": "A model with a similar name already exists.",
                "technical": "Slug already used",
            },
        )
    return ResponseModel.from_orm(model)


@router.patch(
    "/{model_slug}",
    response_model=ResponseModel,
)
def set_tool_details(
    project_slug: str,
    model_slug: str,
    tool_details: ToolDetails,
    db: Session = Depends(get_db),
    token: JWTBearer = Depends(JWTBearer()),
):

    project = projects_crud.get_project_by_slug(db, project_slug)
    if not project:
        raise HTTPException(
            404,
            {
                "reason": f"The project having the name {project_slug} was not found.",
                "technical": f"No project with {project_slug} found.",
            },
        )
    verify_project_role(project.name, token, db, ["manager", "administrator"])
    model = crud.get_model_by_slug(db, project.slug, model_slug)
    if not model:
        raise HTTPException(
            404,
            {
                "reason": f"The model having the name {model_slug} was not found.",
                "technical": f"No model with {model_slug} found in the project {project.name}.",
            },
        )
    try:
        version = tools_crud.get_version_by_id(tool_details.version_id, db)
    except NoResultFound:
        raise HTTPException(
            404,
            {
                "reason": f"The version with id {model.version_id} was not found."
            },
        )
    if version.tool != model.tool:
        raise HTTPException(
            409,
            {
                "reason": f"The tool having the version “{version.name}” (“{version.tool.name}”) does not match the tool of the model “{model.name}” (“{model.tool.name}”)."
            },
        )

    try:
        model_type = tools_crud.get_type_by_id(tool_details.type_id, db)
    except NoResultFound:
        raise HTTPException(
            404, {"reason": f"The type with id {model.type_id} was not found."}
        )
    if model_type.tool != model.tool:
        raise HTTPException(
            409,
            {
                "reason": f"The tool having the type “{model_type.name}” (“{model_type.tool.name}”) does not match the tool of the model “{model.name}” (“{model.tool.name}”)."
            },
        )

    return ResponseModel.from_orm(
        crud.set_tool_details_for_model(
            db,
            model,
            version,
            model_type,
        )
    )
