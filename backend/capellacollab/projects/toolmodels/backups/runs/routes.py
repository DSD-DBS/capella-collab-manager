# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import base64
import datetime
import typing as t

import fastapi
import fastapi_pagination
from apscheduler.triggers import date as ap_date_trigger
from sqlalchemy import orm

from capellacollab import scheduling
from capellacollab.configuration import core as configuration_core
from capellacollab.configuration.app import config
from capellacollab.core import database, responses
from capellacollab.core.logging import exceptions as logging_exceptions
from capellacollab.core.logging import loki
from capellacollab.permissions import models as permissions_models
from capellacollab.projects import exceptions as projects_exceptions
from capellacollab.projects.permissions import (
    injectables as projects_permissions_injectables,
)
from capellacollab.projects.permissions import (
    models as projects_permissions_models,
)
from capellacollab.projects.toolmodels import (
    exceptions as toolmodels_exceptions,
)
from capellacollab.projects.toolmodels.backups import (
    exceptions as backups_exceptions,
)
from capellacollab.users import injectables as user_injectables
from capellacollab.users import models as user_models

from .. import injectables as pipeline_injectables
from .. import models as pipeline_models
from . import crud, exceptions, helper, injectables, interface, models

router = fastapi.APIRouter()


@router.post(
    "",
    status_code=200,
    response_model=models.PipelineRun,
    dependencies=[
        fastapi.Depends(
            projects_permissions_injectables.ProjectPermissionValidation(
                required_scope=projects_permissions_models.ProjectUserScopes(
                    pipeline_runs={permissions_models.UserTokenVerb.CREATE}
                )
            )
        )
    ],
)
def create_pipeline_run(
    pipeline: t.Annotated[
        pipeline_models.DatabasePipeline,
        fastapi.Depends(pipeline_injectables.get_existing_pipeline),
    ],
    triggerer: t.Annotated[
        user_models.DatabaseUser,
        fastapi.Depends(user_injectables.get_own_user),
    ],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
) -> models.DatabasePipelineRun:
    run = crud.create_pipeline_run(
        db,
        models.DatabasePipelineRun(
            pipeline=pipeline,
            triggerer=triggerer,
        ),
    )
    pipeline_config = configuration_core.get_global_configuration(db).pipelines
    scheduling.scheduler.add_job(
        interface.run_job_in_kubernetes,
        trigger=ap_date_trigger.DateTrigger(
            run_date=datetime.datetime.now(datetime.UTC)
        ),
        args=[run.id],
        id=f"job-run-{run.id}",
        name=f"Job run {run.id}",
        coalesce=True,
        misfire_grace_time=pipeline_config.misfire_grace_time,  # Accept unavailable schedules for 1 hour
    )
    return run


@router.get(
    "",
    status_code=200,
    dependencies=[
        fastapi.Depends(
            projects_permissions_injectables.ProjectPermissionValidation(
                required_scope=projects_permissions_models.ProjectUserScopes(
                    pipeline_runs={permissions_models.UserTokenVerb.GET}
                )
            )
        )
    ],
)
def get_pipeline_runs(
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
    pipeline: t.Annotated[
        pipeline_models.DatabasePipeline,
        fastapi.Depends(pipeline_injectables.get_existing_pipeline),
    ],
) -> fastapi_pagination.Page[models.PipelineRun]:
    return crud.get_pipeline_runs_for_pipeline_id_paginated(db, pipeline)


@router.get(
    "/{pipeline_run_id}",
    status_code=200,
    response_model=models.PipelineRun,
    dependencies=[
        fastapi.Depends(
            projects_permissions_injectables.ProjectPermissionValidation(
                required_scope=projects_permissions_models.ProjectUserScopes(
                    pipeline_runs={permissions_models.UserTokenVerb.GET}
                )
            )
        )
    ],
)
def get_pipeline_run(
    pipeline_run: t.Annotated[
        models.DatabasePipelineRun,
        fastapi.Depends(injectables.get_existing_pipeline_run),
    ],
) -> models.DatabasePipelineRun:
    return pipeline_run


@router.get(
    "/{pipeline_run_id}/events",
    responses=responses.translate_exceptions_to_openapi_schema(
        [
            logging_exceptions.GrafanaLokiDisabled,
            logging_exceptions.TooManyOutStandingRequests,
            projects_exceptions.ProjectNotFoundError,
            toolmodels_exceptions.ToolModelNotFound,
            backups_exceptions.PipelineNotFoundError,
            exceptions.PipelineRunNotFoundError,
        ]
    ),
    dependencies=[
        fastapi.Depends(
            projects_permissions_injectables.ProjectPermissionValidation(
                required_scope=projects_permissions_models.ProjectUserScopes(
                    pipeline_runs={permissions_models.UserTokenVerb.GET}
                )
            )
        )
    ],
)
def get_pipeline_run_events(
    pipeline_run: t.Annotated[
        models.DatabasePipelineRun,
        fastapi.Depends(injectables.get_existing_pipeline_run),
    ],
) -> list[models.PipelineEvent]:
    if loki.is_loki_activated():
        event_logs = loki.fetch_logs_from_loki(
            query=f'{{pipeline_run_id="{pipeline_run.id}", job_name="{pipeline_run.reference_id}", log_type="events"}} | logfmt',
            start_time=pipeline_run.trigger_time,
            end_time=_determine_end_time_from_pipeline_run(pipeline_run),
        )
        if not event_logs:
            return []

        return [
            models.PipelineEvent(
                timestamp=_transform_unix_nanoseconds_to_datetime(
                    int(logentry["values"][0][0])
                ),
                message=logentry["stream"]["message"],
                reason=logentry["stream"]["reason"],
            )
            for logentry in event_logs
        ]

    return [
        models.PipelineEvent(
            timestamp=log_line.timestamp,
            reason=log_line.reason,
            message=log_line.line,
        )
        for log_line in pipeline_run.logs
        if log_line.log_type == models.LogType.EVENTS
    ]


def _determine_end_time_from_pipeline_run(
    pipeline_run: models.DatabasePipelineRun,
) -> datetime.datetime:
    max_pipeline_run_duration = datetime.timedelta(
        minutes=config.pipelines.timeout + 5
    )  # Add 5 minutes tolerance to pipeline timeout
    return min(
        pipeline_run.trigger_time.replace(tzinfo=datetime.UTC)
        + max_pipeline_run_duration,
        (pipeline_run.end_time or datetime.datetime.now(datetime.UTC)).replace(
            tzinfo=datetime.UTC
        ),
    )


def _transform_unix_nanoseconds_to_datetime(
    nanoseconds: int,
) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(
        int(nanoseconds) / 10**9, tz=datetime.UTC
    )


@router.get(
    "/{pipeline_run_id}/logs",
    responses=responses.translate_exceptions_to_openapi_schema(
        [
            logging_exceptions.GrafanaLokiDisabled,
            logging_exceptions.TooManyOutStandingRequests,
            projects_exceptions.ProjectNotFoundError,
            toolmodels_exceptions.ToolModelNotFound,
            backups_exceptions.PipelineNotFoundError,
            exceptions.PipelineRunNotFoundError,
        ]
    ),
    dependencies=[
        fastapi.Depends(
            projects_permissions_injectables.ProjectPermissionValidation(
                required_scope=projects_permissions_models.ProjectUserScopes(
                    pipeline_runs={permissions_models.UserTokenVerb.GET}
                )
            )
        )
    ],
)
def get_logs(
    pipeline_run: t.Annotated[
        models.DatabasePipelineRun,
        fastapi.Depends(injectables.get_existing_pipeline_run),
    ],
) -> list[models.PipelineLogLine]:
    if loki.is_loki_activated():
        logs = loki.fetch_logs_from_loki(
            query=f'{{pipeline_run_id="{pipeline_run.id}", job_name="{pipeline_run.reference_id}", log_type="logs"}}',
            start_time=pipeline_run.trigger_time,
            end_time=_determine_end_time_from_pipeline_run(pipeline_run),
        )
        if not logs:
            return []

        logs = [
            models.PipelineLogLine(
                timestamp=_transform_unix_nanoseconds_to_datetime(
                    line["timestamp"]
                ),
                text=line["line"],
            )
            for line in loki.flatten_loki_streams(logs)
        ]
    else:
        logs = [
            models.PipelineLogLine(
                timestamp=log_line.timestamp,
                text=log_line.line,
            )
            for log_line in pipeline_run.logs
            if log_line.log_type == models.LogType.LOGS
        ]

    masked_values = [
        pipeline_run.pipeline.t4c_password,
        pipeline_run.pipeline.t4c_model.repository.instance.password,
    ]
    masked_values_generated = []

    # Also mask derived, e.g. base64 encoded credentials
    for value in masked_values:
        masked_values_generated.append(
            base64.b64encode(value.encode("utf-8")).decode("utf-8")
        )

    helper.filter_logs(logs, masked_values + masked_values_generated)
    return logs


fastapi_pagination.add_pagination(router)
