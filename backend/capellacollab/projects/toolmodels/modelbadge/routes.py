# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import logging

import fastapi
import requests
from aiohttp import web

import capellacollab.projects.toolmodels.modelsources.git.injectables as git_injectables
from capellacollab.core import logging as log
from capellacollab.core import responses
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


@router.get(
    "",
    response_class=fastapi.responses.Response,
    responses=responses.SVGResponse.responses,
)
async def get_model_complexity_badge(
    git_handler: handler.GitHandler = fastapi.Depends(
        git_injectables.get_git_handler
    ),
    logger: logging.LoggerAdapter = fastapi.Depends(log.get_request_logger),
):
    try:
        file = await git_handler.get_file(
            "model-complexity-badge.svg", git_handler.revision
        )
        return responses.SVGResponse(content=file[1])
    except Exception:
        logger.debug(
            "Failed fetching model badge file for %s on revision %s.",
            git_handler.path,
            git_handler.revision,
            exc_info=True,
        )

    try:
        artifact = await git_handler.get_artifact(
            "model-complexity-badge.svg", "generate-model-badge"
        )
        return responses.SVGResponse(content=artifact[2])
    except (web.HTTPError, requests.HTTPError):
        logger.debug(
            "Failed fetching model badge artifact for %s on revision %s.",
            git_handler.path,
            git_handler.revision,
            exc_info=True,
        )
        raise exceptions.ModelBadgeNotConfiguredProperlyError()
