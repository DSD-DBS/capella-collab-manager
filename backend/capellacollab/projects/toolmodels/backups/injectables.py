# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0
import typing as t

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.projects.toolmodels import (
    injectables as toolmodels_injectables,
)
from capellacollab.projects.toolmodels import models as toolmodels_models

from . import crud, exceptions, models


def get_existing_pipeline(
    pipeline_id: int,
    model: t.Annotated[toolmodels_models.DatabaseToolModel, fastapi.Depends(
        toolmodels_injectables.get_existing_capella_model
    )],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
) -> models.DatabaseBackup:
    pipeline = crud.get_pipeline_by_id(db, pipeline_id)

    if pipeline and pipeline.model == model:
        return pipeline

    raise exceptions.PipelineNotFoundError(pipeline_id)
