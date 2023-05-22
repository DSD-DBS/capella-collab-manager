# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import base64
import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.core.database import get_db
from capellacollab.core.logging import loki
from capellacollab.projects.users.models import ProjectUserRole
from capellacollab.users import injectables as user_injectables
from capellacollab.users import models as user_models

from .. import injectables as pipeline_injectables
from ..models import DatabaseBackup
from . import crud, helper, injectables, models

router = APIRouter()


@router.post(
    "",
    status_code=200,
    dependencies=[
        Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=ProjectUserRole.MANAGER
            )
        )
    ],
    response_model=models.PipelineRun,
)
def create_pipeline_run(
    body: models.BackupPipelineRun,
    pipeline: DatabaseBackup = Depends(
        pipeline_injectables.get_existing_pipeline
    ),
    triggerer: user_models.DatabaseUser = Depends(
        user_injectables.get_own_user
    ),
    db: Session = Depends(get_db),
) -> models.DatabasePipelineRun:
    environment = {}
    if body.include_commit_history:
        environment["INCLUDE_COMMIT_HISTORY"] = "true"

    return crud.create_pipeline_run(
        db,
        models.DatabasePipelineRun(
            status=models.PipelineRunStatus.PENDING,
            pipeline=pipeline,
            triggerer=triggerer,
            trigger_time=datetime.datetime.now(),
            environment=environment,
        ),
    )


@router.get(
    "",
    status_code=200,
    dependencies=[
        Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=ProjectUserRole.MANAGER
            )
        )
    ],
    response_model=list[models.PipelineRun],
)
def get_pipeline_runs(
    pipeline: DatabaseBackup = Depends(
        pipeline_injectables.get_existing_pipeline
    ),
) -> list[models.DatabasePipelineRun]:
    return pipeline.runs


@router.get(
    "/{pipeline_run_id}",
    status_code=200,
    dependencies=[
        Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=ProjectUserRole.MANAGER
            )
        )
    ],
    response_model=models.PipelineRun,
)
def get_pipeline_run(
    pipeline_run: DatabaseBackup = Depends(
        injectables.get_existing_pipeline_run
    ),
) -> list[models.DatabasePipelineRun]:
    return pipeline_run


@router.get(
    "/{pipeline_run_id}/events",
    response_model=str,
    dependencies=[
        Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=ProjectUserRole.MANAGER
            )
        )
    ],
)
def get_events(
    pipeline_run: models.DatabasePipelineRun = Depends(
        injectables.get_existing_pipeline_run
    ),
):
    event_logs = loki.fetch_logs_from_loki(
        query=f'{{pipeline_run_id="{pipeline_run.id}", job_name="{pipeline_run.reference_id}", log_type="events"}}',
        start_time=pipeline_run.trigger_time,
        end_time=datetime.datetime.now().astimezone(),
    )
    if not event_logs:
        return ""

    event_logs = "\n".join(
        [
            datetime.datetime.fromtimestamp(
                int(logline[0]) / 10**9
            ).strftime("%Y-%m-%d %H:%M:%S")
            + ": "
            + logline[1]
            for logentry in event_logs
            for logline in logentry["values"]
        ]
    )
    return event_logs


@router.get(
    "/{pipeline_run_id}/logs",
    response_model=str,
    dependencies=[
        Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=ProjectUserRole.MANAGER
            )
        )
    ],
)
def get_logs(
    pipeline_run: models.DatabasePipelineRun = Depends(
        injectables.get_existing_pipeline_run
    ),
):
    logs = loki.fetch_logs_from_loki(
        query=f'{{pipeline_run_id="{pipeline_run.id}", job_name="{pipeline_run.reference_id}", log_type="logs"}}',
        start_time=pipeline_run.trigger_time,
        end_time=datetime.datetime.now().astimezone(),
    )
    if not logs:
        return ""

    logs = "\n".join(
        [
            datetime.datetime.fromtimestamp(
                int(logline[0]) / 10**9
            ).strftime("%Y-%m-%d %H:%M:%S")
            + ": "
            + logline[1]
            for logentry in logs
            for logline in logentry["values"]
        ]
    )

    masked_values = [pipeline_run.pipeline.t4c_password]
    masked_values_generated = []

    # Also mask derivated, e.g. base64 encoded credentials
    for value in masked_values:
        masked_values_generated.append(
            base64.b64encode(value.encode("utf-8")).decode("utf-8")
        )

    return helper.filter_logs(logs, masked_values + masked_values_generated)
