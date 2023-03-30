# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import logging

import fastapi
import requests
from fastapi import status
from sqlalchemy import orm

import capellacollab.projects.toolmodels.modelsources.git.injectables as git_injectables
import capellacollab.projects.toolmodels.modelsources.git.models as git_models
from capellacollab.core import database
from capellacollab.core import logging as log
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.projects.toolmodels.modelsources.git.gitlab import (
    interface as gitlab_interface,
)
from capellacollab.projects.users import models as user_models

router = fastapi.APIRouter(
    dependencies=[
        fastapi.Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=user_models.ProjectUserRole.USER
            )
        )
    ],
)


@router.get("", response_class=fastapi.responses.Response)
def get_model_complexity_badge(
    git_model: git_models.DatabaseGitModel = fastapi.Depends(
        git_injectables.get_existing_primary_git_model
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
    logger: logging.LoggerAdapter = fastapi.Depends(log.get_request_logger),
):
    try:
        return fastapi.responses.Response(
            content=gitlab_interface.get_file_from_repository(
                db,
                "model-complexity-badge.svg",
                git_model,
            ),
            media_type="image/svg+xml",
        )
    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 404:
            raise fastapi.HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "err_code": "COMPLEXITY_BADGE_NOT_FOUND",
                    "reason": (
                        "The model complexity badge integration is not configured properly.",
                        "Please contact your administrator.",
                    ),
                },
            )

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
