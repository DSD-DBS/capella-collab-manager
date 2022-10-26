# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import Session

from capellacollab.core.authentication.database import ProjectRoleVerification
from capellacollab.core.database import get_db
from capellacollab.projects.models import DatabaseProject
from capellacollab.projects.users.models import ProjectUserRole
from capellacollab.tools import crud as tools_crud
from capellacollab.tools.models import Tool, Type, Version

from . import crud
from .injectables import get_existing_capella_model, get_existing_project
from .models import (
    CapellaModel,
    DatabaseCapellaModel,
    ResponseModel,
    ToolDetails,
)
from .modelsources.git.routes import router as router_sources_git
from .modelsources.t4c.routes import router as router_sources_t4c

router = APIRouter(
    dependencies=[
        Depends(ProjectRoleVerification(required_role=ProjectUserRole.USER))
    ],
)


router.include_router(
    router_sources_git,
    prefix="/{model_slug}/git",
    tags=["Projects - Models - Git"],
)
router.include_router(
    router_sources_t4c,
    prefix="/{model_slug}/t4c",
    tags=["Projects - Models - T4C"],
)


@router.get("/", response_model=list[ResponseModel])
def get_models(
    project: DatabaseProject = Depends(get_existing_project),
    db: Session = Depends(get_db),
) -> list[DatabaseCapellaModel]:
    return crud.get_all_models_in_project(db, project)


@router.get("/{model_slug}", response_model=ResponseModel)
def get_model_by_slug(
    model=Depends(get_existing_capella_model),
) -> ResponseModel:
    return model


@router.post(
    "/",
    response_model=ResponseModel,
    dependencies=[
        Depends(ProjectRoleVerification(required_role=ProjectUserRole.MANAGER))
    ],
)
def create_new(
    new_model: CapellaModel,
    project: DatabaseProject = Depends(get_existing_project),
    db: Session = Depends(get_db),
) -> DatabaseCapellaModel:
    tool = get_tool_by_id_or_raise(new_model.tool_id, db)

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
    return model


@router.patch(
    "/{model_slug}",
    response_model=ResponseModel,
    dependencies=[
        Depends(ProjectRoleVerification(required_role=ProjectUserRole.MANAGER))
    ],
)
def set_tool_details(
    tool_details: ToolDetails,
    model: DatabaseCapellaModel = Depends(get_existing_capella_model),
    db: Session = Depends(get_db),
) -> DatabaseCapellaModel:
    version = get_version_by_id_or_raise(db, tool_details.version_id)
    if version.tool != model.tool:
        raise HTTPException(
            409,
            {
                "reason": f"The tool having the version “{version.name}” (“{version.tool.name}”) does not match the tool of the model “{model.name}” (“{model.tool.name}”)."
            },
        )

    model_type = get_type_by_id_or_raise(db, tool_details.type_id)
    if model_type.tool != model.tool:
        raise HTTPException(
            409,
            {
                "reason": f"The tool having the type “{model_type.name}” (“{model_type.tool.name}”) does not match the tool of the model “{model.name}” (“{model.tool.name}”)."
            },
        )

    return crud.set_tool_details_for_model(db, model, version, model_type)


def get_tool_by_id_or_raise(db: Session, tool_id: int) -> Tool:
    try:
        return tools_crud.get_tool_by_id(tool_id, db)
    except NoResultFound:
        raise HTTPException(
            404,
            {"reason": f"The tool with id {tool_id} was not found."},
        )


def get_version_by_id_or_raise(db: Session, version_id: int) -> Version:
    try:
        return tools_crud.get_version_by_id(version_id, db)
    except NoResultFound:
        raise HTTPException(
            404,
            {"reason": f"The version with id {version_id} was not found."},
        )


def get_type_by_id_or_raise(db: Session, type_id: int) -> Type:
    try:
        return tools_crud.get_type_by_id(type_id, db)
    except NoResultFound:
        raise HTTPException(
            404, {"reason": f"The type with id {type_id} was not found."}
        )
