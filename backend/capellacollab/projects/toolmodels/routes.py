# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import uuid

import fastapi
import slugify
from fastapi import status
from sqlalchemy import exc, orm

from capellacollab.core import database
from capellacollab.core import exceptions as core_exceptions
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.projects import injectables as projects_injectables
from capellacollab.projects import models as projects_models
from capellacollab.projects.users import models as projects_users_models
from capellacollab.tools import crud as tools_crud
from capellacollab.tools import injectables as tools_injectables
from capellacollab.tools import models as tools_models
from capellacollab.users import injectables as users_injectables
from capellacollab.users import models as users_models

from . import crud, injectables, models, workspace
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
    "", response_model=list[models.CapellaModel], tags=["Projects - Models"]
)
def get_models(
    project: projects_models.DatabaseProject = fastapi.Depends(
        projects_injectables.get_existing_project
    ),
) -> list[models.DatabaseToolModel]:
    return project.models


@router.get(
    "/{model_slug}",
    response_model=models.CapellaModel,
    tags=["Projects - Models"],
)
def get_model_by_slug(
    model: models.DatabaseToolModel = fastapi.Depends(
        injectables.get_existing_capella_model
    ),
) -> models.DatabaseToolModel:
    return model


@router.post(
    "",
    response_model=models.CapellaModel,
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
    new_model: models.PostCapellaModel,
    project: projects_models.DatabaseProject = fastapi.Depends(
        projects_injectables.get_existing_project
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.DatabaseToolModel:
    tool = tools_injectables.get_existing_tool(
        tool_id=new_model.tool_id, db=db
    )

    configuration = {}
    if tool.integrations and tool.integrations.jupyter:
        configuration["workspace"] = str(uuid.uuid4())

    try:
        model = crud.create_model(
            db, project, new_model, tool, configuration=configuration
        )
    except exc.IntegrityError:
        raise fastapi.HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "reason": f"A model with the name {new_model.name} already exists.",
                "technical": f"The slug '{slugify.slugify(new_model.name)}' is already used",
            },
        )

    if tool.integrations and tool.integrations.jupyter:
        workspace.create_shared_workspace(
            configuration["workspace"], project, model, "2Gi"
        )

    return model


@router.patch(
    "/{model_slug}",
    response_model=models.CapellaModel,
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
    body: models.PatchCapellaModel,
    project: projects_models.DatabaseProject = fastapi.Depends(
        projects_injectables.get_existing_project
    ),
    model: models.DatabaseToolModel = fastapi.Depends(
        injectables.get_existing_capella_model
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
    user: users_models.DatabaseUser = fastapi.Depends(
        users_injectables.get_own_user
    ),
) -> models.DatabaseToolModel:
    if body.name:
        new_slug = slugify.slugify(body.name)

        if model.slug != new_slug and crud.get_model_by_slugs(
            db, project.slug, new_slug
        ):
            raise fastapi.HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "reason": "A model with a similar name already exists.",
                    "technical": "Slug already used",
                },
            )

    version = (
        get_version_by_id_or_raise(db, body.version_id)
        if body.version_id
        else model.version
    )
    if version and body.version_id and version.tool != model.tool:
        raise fastapi.HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "reason": f"The tool '{version.tool.name}' derived from the version '{version.name}' does not match the tool '{model.tool.name}' of the model '{model.name}'."
            },
        )

    nature = (
        get_nature_by_id_or_raise(db, body.nature_id)
        if body.nature_id
        else model.nature
    )
    if nature and body.nature_id and nature.tool != model.tool:
        raise fastapi.HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "reason": f"The tool '{nature.tool.name}' derived from the nature '{nature.name}' does not match the tool '{model.tool.name}' of the model '{model.name}'."
            },
        )

    if body.project_slug:
        new_project = determine_new_project_to_move_model(
            body.project_slug, db, user
        )
        raise_if_model_exists_in_project(model, new_project)
    else:
        new_project = model.project

    return crud.update_model(
        db,
        model,
        body.description,
        body.name,
        version,
        nature,
        new_project,
        body.display_order,
    )


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
        injectables.get_existing_capella_model
    ),
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

    if dependencies:
        raise core_exceptions.ExistingDependenciesError(
            model.name, f"{model.tool.name} model", dependencies
        )

    if (
        model.tool.integrations
        and model.tool.integrations.jupyter
        and model.configuration
        and "workspace" in model.configuration
    ):
        workspace.delete_shared_workspace(model.configuration["workspace"])

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


def determine_new_project_to_move_model(
    project_slug: str, db: orm.Session, user: users_models.DatabaseUser
) -> projects_models.DatabaseProject:
    new_project = projects_injectables.get_existing_project(project_slug, db)
    success = user.role == users_models.Role.ADMIN
    for association in user.projects:
        if association.project_id == new_project.id:
            if (
                not association.role
                == projects_users_models.ProjectUserRole.MANAGER
            ):
                break
            else:
                success = True

    if not success:
        raise fastapi.HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "reason": f"Requesting user does not have permission to move toolmodel to {new_project.slug}"
            },
        )
    return new_project


def raise_if_model_exists_in_project(
    model: models.DatabaseToolModel,
    project: projects_models.DatabaseProject,
):
    if model.slug in [model.slug for model in project.models]:
        raise fastapi.HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "reason": f"Model with name {model.name} already exists in project {project.slug}"
            },
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
