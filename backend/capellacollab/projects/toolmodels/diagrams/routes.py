# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import logging
from urllib import parse

import fastapi
import requests
from fastapi import status
from sqlalchemy import orm

import capellacollab.projects.toolmodels.modelsources.git.injectables as git_injectables
import capellacollab.projects.toolmodels.modelsources.git.models as git_models
from capellacollab.core import database
from capellacollab.core import logging as log
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.projects.toolmodels.diagrams import models
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


@router.get("", response_model=models.DiagramCacheMetadata)
def get_diagram_metadata(
    git_model: git_models.DatabaseGitModel = fastapi.Depends(
        git_injectables.get_existing_primary_git_model
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
    logger: logging.LoggerAdapter = fastapi.Depends(log.get_request_logger),
):
    (
        git_instance,
        project_id,
        last_successful_job,
    ) = gitlab_interface.get_last_job_run_id_for_git_model(
        db, "update_capella_diagram_cache", git_model
    )

    try:
        diagrams = gitlab_interface.get_artifact_from_job_as_json(
            project_id,
            last_successful_job[0],
            "diagram_cache/index.json",
            git_model,
            git_instance,
        )
    except requests.exceptions.HTTPError:
        logger.info("Failed fetching diagram metadata", exc_info=True)
        raise fastapi.HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "reason": (
                    "The diagram cache is not configured properly.",
                    "Please contact your diagram cache administrator.",
                ),
            },
        )

    return {"diagrams": diagrams, "last_updated": last_successful_job[1]}


@router.get("/{diagram_uuid}", response_class=fastapi.responses.Response)
def get_diagram(
    diagram_uuid: str,
    git_model: git_models.DatabaseGitModel = fastapi.Depends(
        git_injectables.get_existing_primary_git_model
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
    logger: logging.LoggerAdapter = fastapi.Depends(log.get_request_logger),
):
    (
        git_instance,
        project_id,
        last_successful_job,
    ) = gitlab_interface.get_last_job_run_id_for_git_model(
        db, "update_capella_diagram_cache", git_model
    )

    try:
        diagram = gitlab_interface.get_artifact_from_job_as_content(
            project_id,
            last_successful_job[0],
            f"diagram_cache/{parse.quote(diagram_uuid, safe='')}.svg",
            git_model,
            git_instance,
        )
    except requests.exceptions.HTTPError:
        logger.info("Failed fetching diagram", exc_info=True)
        raise fastapi.HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
