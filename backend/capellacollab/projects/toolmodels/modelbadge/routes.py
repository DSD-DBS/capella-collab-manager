# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import logging

import aiohttp.web
import fastapi
import requests
from fastapi import status
from sqlalchemy import orm

import capellacollab.projects.toolmodels.modelsources.git.injectables as git_injectables
import capellacollab.projects.toolmodels.modelsources.git.models as git_models
from capellacollab.core import database
from capellacollab.core import logging as log
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.projects.toolmodels.modelsources.git import (
    interface as git_interface,
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


@router.get("", response_class=fastapi.responses.Response)
async def get_model_complexity_badge(
    git_model: git_models.DatabaseGitModel = fastapi.Depends(
        git_injectables.get_existing_primary_git_model
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
    logger: logging.LoggerAdapter = fastapi.Depends(log.get_request_logger),
):
    try:
        return fastapi.responses.Response(
            content=await git_interface.get_file_from_repository(
                db,
                "model-complexity-badge.svg",
                git_model,
            ),
            media_type="image/svg+xml",
        )
    except (aiohttp.web.HTTPException, requests.exceptions.HTTPError):
        logger.info("Failed fetching model complexity badge", exc_info=True)
        raise fastapi.HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "reason": (
                    "The model complexity badge integration is not configured properly.",
                    "Please contact your administrator.",
                ),
            },
        )
