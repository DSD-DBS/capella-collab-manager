# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import logging

import aiohttp.web
import fastapi
import requests

import capellacollab.projects.toolmodels.modelsources.git.injectables as git_injectables
from capellacollab.core import logging as log
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.projects.toolmodels.modelsources.git.handler import handler
from capellacollab.projects.users import models as projects_users_models

from . import exceptions

router = fastapi.APIRouter(
    dependencies=[
        fastapi.Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=projects_users_models.ProjectUserRole.USER
            )
        )
    ],
)


@router.get("", response_class=fastapi.responses.Response)
async def get_model_complexity_badge(
    git_handler: handler.GitHandler = fastapi.Depends(
        git_injectables.get_git_handler
    ),
    logger: logging.LoggerAdapter = fastapi.Depends(log.get_request_logger),
):
    try:
        return fastapi.responses.Response(
            content=(
                await git_handler.get_file_from_repository_or_artifacts(
                    "model-complexity-badge.svg", "generate-model-badge"
                )
            )[1],
            media_type="image/svg+xml",
        )
    except (aiohttp.web.HTTPException, requests.exceptions.HTTPError):
        logger.info("Failed fetching model complexity badge", exc_info=True)
        raise exceptions.ModelBadgeNotConfiguredProperlyError()
