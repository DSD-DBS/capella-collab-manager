# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import asyncio
import logging
import typing as t

import fastapi
from sqlalchemy import orm

import capellacollab.core.logging as core_logging
import capellacollab.projects.crud as projects_crud
import capellacollab.projects.toolmodels.backups.validation as pipelines_validation
import capellacollab.projects.toolmodels.crud as toolmodels_crud
import capellacollab.projects.toolmodels.diagrams.validation as diagrams_validation
import capellacollab.projects.toolmodels.modelbadge.validation as modelbadge_validation
import capellacollab.projects.toolmodels.modelsources.git.validation as git_validation
import capellacollab.projects.toolmodels.validation as toolmodels_validation
import capellacollab.projects.validation as projects_validation
from capellacollab.core import database
from capellacollab.permissions import injectables as permissions_injectables
from capellacollab.permissions import models as permissions_models
from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.sessions import operators
from capellacollab.sessions.hooks import guacamole

from . import models

router = fastapi.APIRouter()


@router.get("/general", response_model=models.StatusResponse)
def general_status(
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
):
    return models.StatusResponse(
        guacamole=guacamole.GuacamoleIntegration.validate_guacamole(),
        database=database.validate_database_session(db),
        operator=operators.get_operator().validate(),
    )


@router.get(
    "/models",
    response_model=list[models.ToolmodelStatus],
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        monitoring={permissions_models.UserTokenVerb.GET}
                    )
                )
            ),
        )
    ],
)
async def model_status(
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
    logger: t.Annotated[
        logging.LoggerAdapter, fastapi.Depends(core_logging.get_request_logger)
    ],
):
    toolmodels = toolmodels_crud.get_models(db)

    tasks_per_model = {
        model.id: _create_tool_model_status_tasks(db, logger, model)
        for model in toolmodels
    }

    return [
        models.ToolmodelStatus(
            project_slug=model.project.slug,
            model_slug=model.slug,
            warnings=toolmodels_validation.calculate_model_warnings(model),
            pipeline_status=pipelines_validation.check_last_pipeline_run_status(
                db, model
            ),
            primary_git_repository_status=await tasks_per_model[model.id][
                "primary_git_repository_status"
            ],
            diagram_cache_status=await tasks_per_model[model.id][
                "diagram_cache_status"
            ],
            model_badge_status=await tasks_per_model[model.id][
                "model_badge_status"
            ],
        )
        for model in toolmodels
    ]


@router.get(
    "/projects",
    response_model=list[models.ProjectStatus],
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        monitoring={permissions_models.UserTokenVerb.GET}
                    )
                )
            ),
        )
    ],
)
def project_status(
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
):
    return [
        models.ProjectStatus(
            project_slug=project.slug,
            warnings=projects_validation.calculate_project_warnings(project),
        )
        for project in projects_crud.get_projects(db)
    ]


def _create_tool_model_status_tasks(
    db: orm.Session,
    logger: logging.LoggerAdapter,
    model: toolmodels_models.DatabaseToolModel,
) -> models.ToolModelStatusTasks:
    return models.ToolModelStatusTasks(
        primary_git_repository_status=asyncio.create_task(
            git_validation.check_primary_git_repository(db, model, logger)
        ),
        model_badge_status=asyncio.create_task(
            modelbadge_validation.check_model_badge_health(db, model, logger)
        ),
        diagram_cache_status=asyncio.create_task(
            diagrams_validation.check_diagram_cache_health(db, model, logger)
        ),
    )
