# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from sqlalchemy import orm

from .. import models as toolmodel_models
from . import crud
from .runs import crud as runs_crud
from .runs import models as runs_models


def check_last_pipeline_run_status(
    db: orm.Session, model: toolmodel_models.DatabaseCapellaModel
) -> runs_models.PipelineRunStatus | None:
    if pipeline := crud.get_first_pipeline_for_tool_model(db, model):
        # Only consider first pipeline for monitoring, usually there is only one pipeline.
        if pipeline_run := runs_crud.get_last_pipeline_run_of_pipeline(
            db, pipeline
        ):
            return pipeline_run.status
    return None
