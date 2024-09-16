# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import logging
import pathlib
from urllib import parse

import fastapi
import requests

import capellacollab.projects.toolmodels.modelsources.git.injectables as git_injectables
from capellacollab.core import logging as log
from capellacollab.core import responses
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.projects.toolmodels.diagrams import models
from capellacollab.projects.toolmodels.modelsources.git.handler import (
    handler as git_handler,
)
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


@router.get("", response_model=models.DiagramCacheMetadata)
async def get_diagram_metadata(
    handler: git_handler.GitHandler = fastapi.Depends(
        git_injectables.get_git_handler
    ),
    logger: logging.LoggerAdapter = fastapi.Depends(log.get_request_logger),
):
    try:
        job_id, last_updated, diagram_metadata_entries = (
            await handler.get_file_or_artifact(
                trusted_file_path="diagram_cache/index.json",
                job_name="update_capella_diagram_cache",
                file_revision=f"diagram-cache/{handler.revision}",
            )
        )
    except requests.HTTPError:
        logger.info(
            "Failed fetching diagram metadata file or artifact for %s",
            handler.path,
            exc_info=True,
        )
        raise exceptions.DiagramCacheNotConfiguredProperlyError()

    diagram_metadata_entries = json.loads(diagram_metadata_entries)
    return models.DiagramCacheMetadata(
        diagrams=[
            models.DiagramMetadata.model_validate(diagram_metadata)
            for diagram_metadata in diagram_metadata_entries
        ],
        last_updated=last_updated,
        job_id=job_id,
    )


@router.get(
    "/{diagram_uuid_or_filename}",
    response_class=fastapi.responses.Response,
    responses=responses.SVGResponse.responses,
)
async def get_diagram(
    diagram_uuid_or_filename: str,
    job_id: str | None = None,
    handler: git_handler.GitHandler = fastapi.Depends(
        git_injectables.get_git_handler
    ),
    logger: logging.LoggerAdapter = fastapi.Depends(log.get_request_logger),
):
    fileextension = pathlib.PurePosixPath(diagram_uuid_or_filename).suffix
    if fileextension and fileextension.lower() != ".svg":
        raise exceptions.FileExtensionNotSupportedError(fileextension)

    diagram_uuid = pathlib.PurePosixPath(diagram_uuid_or_filename).stem
    file_path = f"diagram_cache/{parse.quote(diagram_uuid, safe='')}.svg"

    try:
        file_or_artifact = await handler.get_file_or_artifact(
            trusted_file_path=file_path,
            job_name="update_capella_diagram_cache",
            job_id=job_id,
            file_revision=f"diagram-cache/{handler.revision}",
        )
        return responses.SVGResponse(content=file_or_artifact[2])
    except requests.HTTPError:
        logger.info(
            "Failed fetching diagram file or artifact %s for %s.",
            diagram_uuid,
            handler.path,
            f"diagram-cache/{handler.revision}",
            exc_info=True,
        )
        raise exceptions.DiagramCacheNotConfiguredProperlyError()
