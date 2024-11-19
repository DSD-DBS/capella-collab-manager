# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import logging

import fastapi

import capellacollab.projects.toolmodels.modelsources.git.injectables as git_injectables
from capellacollab.core import logging as log
from capellacollab.core import responses
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.projects.toolmodels.modelsources.git.handler import handler
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


@router.get(
    "",
    response_class=fastapi.responses.Response,
    responses=responses.MarkdownResponse.responses,
)
async def get_readme(
    git_handler: handler.GitHandler = fastapi.Depends(
        git_injectables.get_git_handler
    ),
    logger: logging.LoggerAdapter = fastapi.Depends(log.get_request_logger),
):
    _, file = await git_handler.get_file("README.md", logger, None)
    return responses.MarkdownResponse(content=file)
