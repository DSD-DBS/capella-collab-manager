# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import uuid

import fastapi
import slugify
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core import exceptions as core_exceptions
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.projects import injectables as projects_injectables
from capellacollab.projects import models as projects_models
from capellacollab.projects.toolmodels.modelsources.t4c import util as t4c_util
from capellacollab.projects.users import models as projects_users_models
from capellacollab.tools import injectables as tools_injectables
from capellacollab.users import injectables as users_injectables
from capellacollab.users import models as users_models

from . import crud, exceptions, injectables, models, workspace
from .backups import routes as backups_routes
from .diagrams import routes as diagrams_routes
from .modelbadge import routes as complexity_badge_routes
from .modelsources import routes as modelsources_routes
from .provisioning import routes as provisioning_routes
from .readme import routes as readme_routes
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
    "", response_model=list[models.ToolModel], tags=["Projects - Models"]
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
        injectables.get_existing_capella_model
    ),
) -> models.DatabaseToolModel:
    return model


@router.post(
    "",
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
    configuration = {}
    if tool.integrations.jupyter:
        configuration["workspace"] = str(uuid.uuid4())

    slug = slugify.slugify(new_model.name)
    if project.type not in tool.config.supported_project_types:
        raise exceptions.ProjectTypeNotSupportedByToolModel(project.slug, slug)
    if crud.get_model_by_slugs(db, project.slug, slug):
        raise exceptions.ToolModelAlreadyExistsError(project.slug, slug)

    model = crud.create_model(
        db, project, new_model, tool, configuration=configuration
    )

    if tool.integrations.jupyter:
        workspace.create_shared_workspace(
            configuration["workspace"], project, model, "2Gi"
        )

    return model


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
            raise exceptions.ToolModelAlreadyExistsError(
                project.slug, new_slug
            )

    version = (
        tools_injectables.get_existing_tool_version(
            model.tool_id, body.version_id, db
        )
        if body.version_id
        else model.version
    )

    nature = (
        tools_injectables.get_existing_tool_nature(
            model.tool_id, body.nature_id, db
        )
        if body.nature_id
        else model.nature
    )

    for t4c_model in model.t4c_models:
        t4c_util.verify_compatibility_of_model_and_server(
            model.name, version, t4c_model.repository
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
            f"{len(model.git_models)} linked Git repositor{'y' if len(model.git_models) == 1 else 'ies'}"  # codespell:ignore
        )

    if model.t4c_models:
        dependencies.append(
            f"{len(model.t4c_models)} linked T4C repositor{'y' if len(model.t4c_models) == 1 else 'ies'}"  # codespell:ignore
        )

    if dependencies:
        raise core_exceptions.ExistingDependenciesError(
            model.name, f"{model.tool.name} model", dependencies
        )

    if (
        model.tool.integrations.jupyter
        and model.configuration
        and "workspace" in model.configuration
    ):
        workspace.delete_shared_workspace(model.configuration["workspace"])

    crud.delete_model(db, model)


def determine_new_project_to_move_model(
    project_slug: str, db: orm.Session, user: users_models.DatabaseUser
) -> projects_models.DatabaseProject:
    new_project = projects_injectables.get_existing_project(project_slug, db)

    auth_injectables.ProjectRoleVerification(
        required_role=projects_users_models.ProjectUserRole.MANAGER
    )(project_slug, user.name, db)

    return new_project


def raise_if_model_exists_in_project(
    model: models.DatabaseToolModel,
    project: projects_models.DatabaseProject,
):
    if model.slug in [model.slug for model in project.models]:
        raise exceptions.ToolModelAlreadyExistsError(project.slug, model.slug)


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
router.include_router(
    provisioning_routes.router,
    prefix="/{model_slug}/provisioning",
    tags=["Projects - Models - Provisioning"],
)
router.include_router(
    readme_routes.router,
    prefix="/{model_slug}/readme",
    tags=["Projects - Models - README"],
)
