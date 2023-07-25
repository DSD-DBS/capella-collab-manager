# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import logging

import fastapi
from sqlalchemy import orm

import capellacollab.settings.modelsources.git.core as git_core

from ... import models as toolmodels_models
from . import crud, models
from .handler import factory


async def check_primary_git_repository(
    db: orm.Session,
    model: toolmodels_models.DatabaseCapellaModel,
    log: logging.LoggerAdapter,
) -> models.GitModelStatus:
    primary_repo = crud.get_primary_git_model_of_capellamodel(db, model.id)
    if not primary_repo:
        return models.GitModelStatus.UNSET

    try:
        await git_core.get_remote_refs(
            primary_repo.path,
            primary_repo.username,
            primary_repo.password,
            default=primary_repo.revision,
        )
    except:  # pylint: disable=bare-except
        log.debug(
            "Failed to access git model for model with slug '%s' and id %d",
            model.slug,
            model.id,
            exc_info=True,
        )
        return models.GitModelStatus.INACCESSIBLE

    return models.GitModelStatus.ACCESSIBLE


async def check_pipeline_health(
    db: orm.Session,
    model: toolmodels_models.DatabaseCapellaModel,
    job_name: str,
    logger: logging.LoggerAdapter,
) -> models.ModelArtifactStatus:
    primary_git_model = crud.get_primary_git_model_of_capellamodel(
        db, model.id
    )
    if not primary_git_model:
        return models.ModelArtifactStatus.UNCONFIGURED

    try:
        git_handler = factory.GitHandlerFactory.create_git_handler(
            db, primary_git_model
        )
        await git_handler.get_last_job_run_id_for_git_model(job_name)
    except fastapi.HTTPException as e:
        match e.detail.get("err_code", ""):
            case (
                "NO_SUCCESSFUL_JOB"
                | "NO_MATCHING_GIT_INSTANCE"
                | "GIT_INSTANCE_NO_API_ENDPOINT_DEFINED"
                | "ACCESS_DENIED"
                | "PROJECT_NOT_FOUND"
            ):
                print(e.detail.get("err_code", ""))
                return models.ModelArtifactStatus.FAILURE
            case "GIT_INSTANCE_UNSUPPORTED":
                return models.ModelArtifactStatus.UNSUPPORTED
            case "PIPELINE_JOB_NOT_FOUND":
                return models.ModelArtifactStatus.UNCONFIGURED
            case _:
                return models.ModelArtifactStatus.FAILURE
    except:  # pylint: disable=bare-except
        logger.error(
            f"Failed to fetch artifacts for model '{model.slug}' and job '{job_name}'",
            exc_info=True,
        )
        return models.ModelArtifactStatus.FAILURE

    return models.ModelArtifactStatus.SUCCESS
