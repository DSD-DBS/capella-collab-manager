# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import logging

from sqlalchemy import orm

import capellacollab.projects.toolmodels.models as toolmodels_models
import capellacollab.projects.toolmodels.modelsources.git.gitlab.models as gitlab_models
import capellacollab.projects.toolmodels.modelsources.git.gitlab.validation as gitlab_validation


async def check_model_badge_health(
    db: orm.Session,
    model: toolmodels_models.DatabaseCapellaModel,
    logger: logging.LoggerAdapter,
) -> gitlab_models.ModelArtifactStatus:
    return await gitlab_validation.check_pipeline_health(
        db, model, "generate-model-badge", logger
    )
