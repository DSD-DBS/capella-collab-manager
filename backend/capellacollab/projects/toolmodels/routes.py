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
from capellacollab.tools.models import Nature, Tool, Version

from . import crud
from .backups.routes import router as router_backups
from .injectables import get_existing_capella_model, get_existing_project
from .models import (
    CapellaModel,
    DatabaseCapellaModel,
    PatchCapellaModel,
    PostCapellaModel,
)
from .modelsources.routes import router as router_modelsources
from .restrictions.routes import router as router_restrictions

router = APIRouter(
    dependencies=[
        Depends(ProjectRoleVerification(required_role=ProjectUserRole.USER))
    ],
)


@router.get("/", response_model=list[CapellaModel], tags=["Projects - Models"])
def get_models(
    project: DatabaseProject = Depends(get_existing_project),
) -> list[DatabaseCapellaModel]:
    return project.models


@router.get(
    "/{model_slug}", response_model=CapellaModel, tags=["Projects - Models"]
)
def get_model_by_slug(
    model: DatabaseCapellaModel = Depends(get_existing_capella_model),
) -> DatabaseCapellaModel:
    return model


@router.post(
    "/",
    response_model=CapellaModel,
    dependencies=[
        Depends(ProjectRoleVerification(required_role=ProjectUserRole.MANAGER))
    ],
    tags=["Projects - Models"],
)
def create_new(
    new_model: PostCapellaModel,
    project: DatabaseProject = Depends(get_existing_project),
    db: Session = Depends(get_db),
) -> DatabaseCapellaModel:
    tool = get_tool_by_id_or_raise(db, new_model.tool_id)

    try:
        return crud.create_new_model(db, project, new_model, tool)
    except IntegrityError:
        raise HTTPException(
            409,
            {
                "reason": "A model with a similar name already exists.",
                "technical": "Slug already used",
            },
        )


@router.patch(
    "/{model_slug}",
    response_model=CapellaModel,
    dependencies=[
        Depends(ProjectRoleVerification(required_role=ProjectUserRole.MANAGER))
    ],
    tags=["Projects - Models"],
)
def patch_capella_model(
    body: PatchCapellaModel,
    model: DatabaseCapellaModel = Depends(get_existing_capella_model),
    db: Session = Depends(get_db),
) -> DatabaseCapellaModel:

    version = get_version_by_id_or_raise(db, body.version_id)
    if version.tool != model.tool:
        raise HTTPException(
            409,
            {
                "reason": f"The tool having the version “{version.name}” (“{version.tool.name}”) does not match the tool of the model “{model.name}” (“{model.tool.name}”)."
            },
        )

    nature = get_nature_by_id_or_raise(db, body.nature_id)
    if nature.tool != model.tool:
        raise HTTPException(
            409,
            {
                "reason": f"The tool having the nature “{nature.name}” (“{nature.tool.name}”) does not match the tool of the model “{model.name}” (“{model.tool.name}”)."
            },
        )

    return crud.update_model(db, model, body.description, version, nature)


@router.delete(
    "/{model_slug}",
    status_code=204,
    dependencies=[
        Depends(ProjectRoleVerification(required_role=ProjectUserRole.MANAGER))
    ],
    tags=["Projects - Models"],
)
def delete_capella_model(
    model: DatabaseCapellaModel = Depends(get_existing_capella_model),
    db: Session = Depends(get_db),
):
    if not (model.git_models or model.t4c_models):
        crud.delete_model(db, model)


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


def get_nature_by_id_or_raise(db: Session, nature_id: int) -> Nature:
    try:
        return tools_crud.get_nature_by_id(nature_id, db)
    except NoResultFound:
        raise HTTPException(
            404, {"reason": f"The nature with id {nature_id} was not found."}
        )


router.include_router(
    router_modelsources,
    prefix="/{model_slug}/modelsources",
)
router.include_router(
    router_backups,
    prefix="/{model_slug}/backups/pipelines",
    tags=["Projects - Models - Backups"],
)
router.include_router(
    router_restrictions,
    prefix="/{model_slug}/restrictions",
    tags=["Projects - Models - Restrictions"],
)
