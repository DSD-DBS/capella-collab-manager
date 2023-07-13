# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import logging

from sqlalchemy import orm

import capellacollab.settings.modelsources.git.core as git_core

from ... import models as toolmodels_models
from . import crud, models


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
