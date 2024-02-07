# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging

from sqlalchemy import orm

import capellacollab.projects.toolmodels.models as toolmodels_models
import capellacollab.projects.toolmodels.modelsources.git.models as git_models
import capellacollab.projects.toolmodels.modelsources.git.validation as git_validation


async def check_diagram_cache_health(
    db: orm.Session,
    model: toolmodels_models.DatabaseToolModel,
    logger: logging.LoggerAdapter,
) -> git_models.ModelArtifactStatus:
    return await git_validation.check_pipeline_health(
        db, model, "update_capella_diagram_cache", logger
    )
