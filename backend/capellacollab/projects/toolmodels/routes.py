# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from fastapi import status
from sqlalchemy import exc, orm

from capellacollab.core import database
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.projects import injectables as projects_injectables
from capellacollab.projects import models as projects_models
from capellacollab.projects.users import models as projects_users_models
from capellacollab.tools import crud as tools_crud
from capellacollab.tools import injectables as tools_injectables
from capellacollab.tools import models as tools_models

from . import crud, injectables, models
from .backups import routes as backups_routes
from .diagrams import routes as diagrams_routes
from .modelbadge import routes as complexity_badge_routes
from .modelsources import routes as modelsources_routes
from .restrictions import routes as restrictions_routes

router = fastapi.APIRouter(
    dependencies=[
        fastapi.Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=projects_users_models.ProjectUserRole.USER
            )
        )
    ],
)


@router.get(
    "/", response_model=list[models.ToolModel], tags=["Projects - Models"]
)
def get_models(
    project: projects_models.DatabaseProject = fastapi.Depends(
        projects_injectables.get_existing_project
    ),
) -> list[models.DatabaseToolModel]:
    return project.models


@router.get(
    "/{model_slug}",
    response_model=models.ToolModel,
    tags=["Projects - Models"],
)
def get_model_by_slug(
    model: models.DatabaseToolModel = fastapi.Depends(
        injectables.get_existing_tool_model
    ),
) -> models.DatabaseToolModel:
    return model


@router.post(
    "/",
    response_model=models.ToolModel,
    dependencies=[
        fastapi.Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=projects_users_models.ProjectUserRole.MANAGER
            )
        )
    ],
    tags=["Projects - Models"],
)
def create_new_tool_model(
    new_model: models.PostToolModel,
    project: projects_models.DatabaseProject = fastapi.Depends(
        projects_injectables.get_existing_project
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.DatabaseToolModel:
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
    response_model=models.ToolModel,
    dependencies=[
        fastapi.Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=projects_users_models.ProjectUserRole.MANAGER
            )
        )
    ],
    tags=["Projects - Models"],
)
def patch_tool_model(
    body: models.PatchToolModel,
    model: models.DatabaseToolModel = fastapi.Depends(
        injectables.get_existing_tool_model
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.DatabaseToolModel:
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
                required_role=projects_users_models.ProjectUserRole.MANAGER
            )
        )
    ],
    tags=["Projects - Models"],
)
def delete_tool_model(
    model: models.DatabaseToolModel = fastapi.Depends(
        injectables.get_existing_tool_model
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    if not (model.git_models or model.t4c_models):
        crud.delete_model(db, model)


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
    modelsources_routes.router,
    prefix="/{model_slug}/modelsources",
)
router.include_router(
    backups_routes.router,
    prefix="/{model_slug}/backups/pipelines",
    tags=["Projects - Models - Backups"],
)
router.include_router(
    restrictions_routes.router,
    prefix="/{model_slug}/restrictions",
    tags=["Projects - Models - Restrictions"],
)
router.include_router(
    diagrams_routes.router,
    prefix="/{model_slug}/diagrams",
    tags=["Projects - Models - Diagrams"],
)
router.include_router(
    complexity_badge_routes.router,
    prefix="/{model_slug}/badges/complexity",
    tags=["Projects - Models - Model complexity badge"],
)
