# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import logging
from urllib import parse

import fastapi
import requests
from fastapi import status

import capellacollab.projects.toolmodels.modelsources.git.injectables as git_injectables
from capellacollab.core import logging as log
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.projects.toolmodels.diagrams import models
from capellacollab.projects.toolmodels.modelsources.git.handler import (
    handler as git_handler,
)
from capellacollab.projects.users import models as projects_users_models

router = fastapi.APIRouter(
    dependencies=[
        fastapi.Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=projects_users_models.ProjectUserRole.USER
            )
        )
    ],
)


@router.get("", response_model=models.DiagramCacheMetadata)
async def get_diagram_metadata(
    handler: git_handler.GitHandler = fastapi.Depends(
        git_injectables.get_git_handler
    ),
    logger: logging.LoggerAdapter = fastapi.Depends(log.get_request_logger),
):
    (
        project_id,
        last_successful_job,
    ) = await handler.get_last_job_run_id_for_git_model(
        "update_capella_diagram_cache"
    )
    try:
        diagrams = handler.get_artifact_from_job_as_json(
            project_id,
            last_successful_job[0],
            "diagram_cache/index.json",
        )
    except requests.exceptions.HTTPError:
        logger.info("Failed fetching diagram metadata", exc_info=True)
        raise fastapi.HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "reason": (
                    "The diagram cache is not configured properly.",
                    "Please contact your diagram cache administrator.",
                ),
            },
        )

    return models.DiagramCacheMetadata(
        diagrams=diagrams, last_updated=last_successful_job[1]
    )


@router.get("/{diagram_uuid}", response_class=fastapi.responses.Response)
async def get_diagram(
    diagram_uuid: str,
    handler: git_handler.GitHandler = fastapi.Depends(
        git_injectables.get_git_handler
    ),
    logger: logging.LoggerAdapter = fastapi.Depends(log.get_request_logger),
):
    (
        project_id,
        last_successful_job,
    ) = await handler.get_last_job_run_id_for_git_model(
        "update_capella_diagram_cache"
    )

    try:
        diagram = handler.get_artifact_from_job_as_content(
            project_id,
            last_successful_job[0],
            f"diagram_cache/{parse.quote(diagram_uuid, safe='')}.svg",
        )
    except requests.exceptions.HTTPError:
        logger.info("Failed fetching diagram", exc_info=True)
        raise fastapi.HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "reason": (
                    "The diagram cache is not configured properly.",
                    "Please contact your diagram cache administrator.",
                ),
            },
        )

    return fastapi.responses.Response(
        content=diagram,
        media_type="image/svg+xml",
    )
