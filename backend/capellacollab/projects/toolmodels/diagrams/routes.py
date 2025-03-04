# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import logging
import pathlib
import typing as t
from urllib import parse

import fastapi
import requests

import capellacollab.projects.toolmodels.modelsources.git.injectables as git_injectables
from capellacollab.core import responses
from capellacollab.core.logging import injectables as logging_injectables
from capellacollab.permissions import models as permissions_models
from capellacollab.projects.permissions import (
    injectables as projects_permissions_injectables,
)
from capellacollab.projects.permissions import (
    models as projects_permissions_models,
)
from capellacollab.projects.toolmodels.diagrams import models
from capellacollab.projects.toolmodels.modelsources.git.handler import (
    handler as git_handler,
)

from . import core, exceptions

router = fastapi.APIRouter()


@router.get(
    "",
    response_model=models.DiagramCacheMetadata,
    dependencies=[
        fastapi.Depends(
            projects_permissions_injectables.ProjectPermissionValidation(
                required_scope=projects_permissions_models.ProjectUserScopes(
                    diagram_cache={permissions_models.UserTokenVerb.GET}
                )
            )
        )
    ],
)
async def get_diagram_metadata(
    handler: t.Annotated[
        git_handler.GitHandler,
        fastapi.Depends(git_injectables.get_git_handler),
    ],
    logger: t.Annotated[
        logging.LoggerAdapter,
        fastapi.Depends(logging_injectables.get_request_logger),
    ],
):
    (
        job_id,
        last_updated,
        diagram_metadata_entries,
    ) = await core.fetch_diagram_cache_metadata(logger, handler)

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
    dependencies=[
        fastapi.Depends(
            projects_permissions_injectables.ProjectPermissionValidation(
                required_scope=projects_permissions_models.ProjectUserScopes(
                    diagram_cache={permissions_models.UserTokenVerb.GET}
                )
            )
        )
    ],
)
async def get_diagram(
    diagram_uuid_or_filename: str,
    handler: t.Annotated[
        git_handler.GitHandler,
        fastapi.Depends(git_injectables.get_git_handler),
    ],
    logger: t.Annotated[
        logging.LoggerAdapter,
        fastapi.Depends(logging_injectables.get_request_logger),
    ],
    job_id: str | None = None,
):
    fileextension = pathlib.PurePosixPath(diagram_uuid_or_filename).suffix
    if fileextension and fileextension.lower() != ".svg":
        raise exceptions.FileExtensionNotSupportedError(fileextension)

    diagram_uuid = pathlib.PurePosixPath(diagram_uuid_or_filename).stem

    (
        job_id,
        _,
        diagram_metadata_entries,
    ) = await core.fetch_diagram_cache_metadata(logger, handler, job_id)

    diagrams = [
        models.DiagramMetadata.model_validate(diagram_metadata)
        for diagram_metadata in json.loads(diagram_metadata_entries)
    ]

    try:
        diagram = next(
            diagram for diagram in diagrams if diagram.uuid == diagram_uuid
        )
    except StopIteration:
        raise exceptions.DiagramNotFoundError(diagram_uuid) from None

    if not diagram.success:
        raise exceptions.DiagramNotSuccessfulError(diagram_uuid)

    file_path = f"diagram_cache/{parse.quote(diagram_uuid, safe='')}.svg"

    try:
        file_or_artifact = await handler.get_file_or_artifact(
            trusted_file_path=file_path,
            logger=logger,
            job_name="update_capella_diagram_cache",
            job_id=job_id,
            file_revision=f"diagram-cache/{handler.revision}",
        )
        return responses.SVGResponse(content=file_or_artifact[2])
    except requests.HTTPError as e:
        logger.info(
            "Failed fetching diagram file or artifact %s for %s.",
            diagram_uuid,
            f"diagram-cache/{handler.revision}",
            exc_info=True,
        )
        raise exceptions.DiagramCacheNotConfiguredProperlyError() from e
