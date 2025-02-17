# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import logging
import typing as t

import fastapi

import capellacollab.projects.toolmodels.modelsources.git.injectables as git_injectables
from capellacollab.core import logging as log
from capellacollab.core import responses
from capellacollab.permissions import models as permissions_models
from capellacollab.projects.permissions import (
    injectables as projects_permissions_injectables,
)
from capellacollab.projects.permissions import (
    models as projects_permissions_models,
)
from capellacollab.projects.toolmodels.modelsources.git.handler import handler

router = fastapi.APIRouter()


@router.get(
    "",
    response_class=fastapi.responses.Response,
    responses=responses.MarkdownResponse.responses,
    dependencies=[
        fastapi.Depends(
            projects_permissions_injectables.ProjectPermissionValidation(
                required_scope=projects_permissions_models.ProjectUserScopes(
                    tool_models={permissions_models.UserTokenVerb.GET}
                )
            )
        )
    ],
)
async def get_readme(
    git_handler: t.Annotated[
        handler.GitHandler, fastapi.Depends(git_injectables.get_git_handler)
    ],
    logger: t.Annotated[
        logging.LoggerAdapter, fastapi.Depends(log.get_request_logger)
    ],
):
    _, file = await git_handler.get_file("README.md", logger, None)
    return responses.MarkdownResponse(content=file)
