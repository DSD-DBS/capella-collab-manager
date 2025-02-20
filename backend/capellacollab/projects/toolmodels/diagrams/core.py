# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import logging

import requests
from sqlalchemy import orm

from capellacollab.projects.toolmodels.modelsources.git import (
    models as git_models,
)
from capellacollab.projects.toolmodels.modelsources.git.handler import (
    factory as git_handler_factory,
)
from capellacollab.projects.toolmodels.modelsources.git.handler import (
    handler as git_handler,
)
from capellacollab.sessions import util as sessions_util

from . import exceptions


async def fetch_diagram_cache_metadata(
    logger: logging.LoggerAdapter,
    handler: git_handler.GitHandler,
    job_id: str | None = None,
) -> tuple[str | None, datetime.datetime, bytes]:
    try:
        return await handler.get_file_or_artifact(
            trusted_file_path="diagram_cache/index.json",
            logger=logger,
            job_name="update_capella_diagram_cache",
            file_revision=f"diagram-cache/{handler.revision}",
            job_id=job_id,
        )
    except requests.HTTPError as e:
        logger.info(
            "Failed fetching diagram metadata file or artifact for %s",
            handler.path,
            exc_info=True,
        )
        raise exceptions.DiagramCacheNotConfiguredProperlyError() from e


async def build_diagram_cache_api_url(
    logger: logging.LoggerAdapter,
    git_repository: git_models.DatabaseGitModel,
    db: orm.Session,
    revision: str | None = None,
) -> str:
    handler = await git_handler_factory.GitHandlerFactory.create_git_handler(
        db, git_repository, revision
    )
    (job_id, _, _) = await fetch_diagram_cache_metadata(logger, handler)

    job_id_query = f"?job_id={job_id}" if job_id else ""
    return (
        f"{sessions_util.get_api_base_url()}/v1/projects"
        f"/{git_repository.model.project.slug}/models/{git_repository.model.slug}"
        f"/diagrams/%s{job_id_query}"
    )
