# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from fastapi import status
from sqlalchemy import exc, orm

from capellacollab.core import database
from capellacollab.core import exceptions as core_exceptions
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.projects import injectables as projects_injectables
from capellacollab.projects.models import DatabaseProject
from capellacollab.projects.users.models import ProjectUserRole
from capellacollab.tools import crud as tools_crud
from capellacollab.tools import injectables as tools_injectables
from capellacollab.tools import models as tools_models

from . import crud
from .backups.routes import router as router_backups
from .diagrams.routes import router as router_diagrams
from .injectables import get_existing_capella_model
from .modelbadge.routes import router as router_complexity_badge
from .models import (
    CapellaModel,
    DatabaseCapellaModel,
    PatchCapellaModel,
    PostCapellaModel,
)
from .modelsources.routes import router as router_modelsources
from .restrictions.routes import router as router_restrictions

router = fastapi.APIRouter(
    dependencies=[
        fastapi.Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=ProjectUserRole.USER
            )
        )
    ],
)


@router.get("/", response_model=list[CapellaModel], tags=["Projects - Models"])
def get_models(
    project: DatabaseProject = fastapi.Depends(
        projects_injectables.get_existing_project
    ),
) -> list[DatabaseCapellaModel]:
    return project.models


@router.get(
    "/{model_slug}", response_model=CapellaModel, tags=["Projects - Models"]
)
def get_model_by_slug(
    model: DatabaseCapellaModel = fastapi.Depends(get_existing_capella_model),
) -> DatabaseCapellaModel:
    return model


@router.post(
    "/",
    response_model=CapellaModel,
    dependencies=[
        fastapi.Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=ProjectUserRole.MANAGER
            )
        )
    ],
    tags=["Projects - Models"],
)
def create_new(
    new_model: PostCapellaModel,
    project: DatabaseProject = fastapi.Depends(
        projects_injectables.get_existing_project
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> DatabaseCapellaModel:
    tool = tools_injectables.get_existing_tool(
        tool_id=new_model.tool_id, db=db
    )

    try:
        return crud.create_model(db, project, new_model, tool)
    except exc.IntegrityError:
        raise fastapi.HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "reason": "A model with a similar name already exists.",
                "technical": "Slug already used",
            },
        )


@router.patch(
    "/{model_slug}",
    response_model=CapellaModel,
    dependencies=[
        fastapi.Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=ProjectUserRole.MANAGER
            )
        )
    ],
    tags=["Projects - Models"],
)
def patch_capella_model(
    body: PatchCapellaModel,
    model: DatabaseCapellaModel = fastapi.Depends(get_existing_capella_model),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> DatabaseCapellaModel:
    version = get_version_by_id_or_raise(db, body.version_id)
    if version.tool != model.tool:
        raise fastapi.HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "reason": f"The tool having the version “{version.name}” (“{version.tool.name}”) does not match the tool of the model “{model.name}” (“{model.tool.name}”)."
            },
        )

    nature = get_nature_by_id_or_raise(db, body.nature_id)
    if nature.tool != model.tool:
        raise fastapi.HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "reason": f"The tool having the nature “{nature.name}” (“{nature.tool.name}”) does not match the tool of the model “{model.name}” (“{model.tool.name}”)."
            },
        )

    return crud.update_model(db, model, body.description, version, nature)


@router.delete(
    "/{model_slug}",
    status_code=204,
    dependencies=[
        fastapi.Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=ProjectUserRole.MANAGER
            )
        )
    ],
    tags=["Projects - Models"],
)
def delete_capella_model(
    model: DatabaseCapellaModel = fastapi.Depends(get_existing_capella_model),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    dependencies = []

    if model.git_models:
        dependencies.append(
            f"{len(model.git_models)} linked Git repositor{'y' if len(model.git_models) == 1 else 'ies'}"
        )

    if model.t4c_models:
        dependencies.append(
            f"{len(model.t4c_models)} linked T4C repositor{'y' if len(model.t4c_models) == 1 else 'ies'}"
        )

    if not dependencies:
        crud.delete_model(db, model)
    else:
        raise core_exceptions.ExistingDependenciesError(
            model.name, f"{model.tool.name} model", dependencies
        )


def get_version_by_id_or_raise(
    db: orm.Session, version_id: int
) -> tools_models.DatabaseVersion:
    if version := tools_crud.get_version_by_id(db, version_id):
        return version

    raise fastapi.HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"reason": f"The version with id {version_id} was not found."},
    )


def get_nature_by_id_or_raise(
    db: orm.Session, nature_id: int
) -> tools_models.DatabaseNature:
    if nature := tools_crud.get_nature_by_id(db, nature_id):
        return nature

    raise fastapi.HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"reason": f"The nature with id {nature_id} was not found."},
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
router.include_router(
    router_diagrams,
    prefix="/{model_slug}/diagrams",
    tags=["Projects - Models - Diagrams"],
)
router.include_router(
    router_complexity_badge,
    prefix="/{model_slug}/badges/complexity",
    tags=["Projects - Models - Model complexity badge"],
)
