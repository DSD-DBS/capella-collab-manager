# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import logging
import typing as t
import uuid

import fastapi
import requests
from sqlalchemy import orm

from capellacollab.core import credentials, database
from capellacollab.permissions import injectables as permissions_injectables
from capellacollab.permissions import models as permissions_models
from capellacollab.projects.permissions import (
    injectables as projects_permissions_injectables,
)
from capellacollab.projects.permissions import (
    models as projects_permissions_models,
)
from capellacollab.projects.toolmodels import (
    injectables as toolmodels_injectables,
)
from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.projects.toolmodels.modelsources.git import (
    injectables as git_injectables,
)
from capellacollab.projects.toolmodels.modelsources.t4c import (
    injectables as t4c_injectables,
)
from capellacollab.settings.modelsources.t4c.instance.repositories import (
    interface as t4c_repository_interface,
)

from .. import exceptions as toolmodels_exceptions
from . import core, crud, exceptions, injectables, interface, models
from .runs import routes as runs_routes

router = fastapi.APIRouter()
log = logging.getLogger(__name__)


def add_next_run_to_pipeline[T: models.Pipeline | models.ExtendedPipeline](
    pipeline: T,
) -> T:
    """Add the next run time to the pipeline model."""
    if not pipeline.run_nightly:
        return pipeline

    job = interface.get_scheduled_pipeline_job(pipeline)
    if not job:
        return pipeline

    if hasattr(job, "next_run_time") and job.next_run_time:
        pipeline.next_run = job.next_run_time.astimezone(datetime.UTC)
    return pipeline


@router.get(
    "",
    dependencies=[
        fastapi.Depends(
            projects_permissions_injectables.ProjectPermissionValidation(
                required_scope=projects_permissions_models.ProjectUserScopes(
                    pipelines={permissions_models.UserTokenVerb.GET}
                )
            )
        )
    ],
)
def get_pipelines(
    model: t.Annotated[
        toolmodels_models.DatabaseToolModel,
        fastapi.Depends(toolmodels_injectables.get_existing_capella_model),
    ],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
) -> list[models.Pipeline]:
    return [
        add_next_run_to_pipeline(models.Pipeline.model_validate(pipeline))
        for pipeline in crud.get_pipelines_for_tool_model(db, model)
    ]


@router.get(
    "/{pipeline_id}",
    dependencies=[
        fastapi.Depends(
            projects_permissions_injectables.ProjectPermissionValidation(
                required_scope=projects_permissions_models.ProjectUserScopes(
                    pipelines={permissions_models.UserTokenVerb.GET}
                )
            )
        )
    ],
)
def get_pipeline(
    pipeline: t.Annotated[
        models.DatabasePipeline,
        fastapi.Depends(injectables.get_existing_pipeline),
    ],
) -> models.Pipeline:
    return add_next_run_to_pipeline(models.Pipeline.model_validate(pipeline))


@router.post(
    "",
    dependencies=[
        fastapi.Depends(
            projects_permissions_injectables.ProjectPermissionValidation(
                required_scope=projects_permissions_models.ProjectUserScopes(
                    pipelines={permissions_models.UserTokenVerb.CREATE}
                )
            )
        )
    ],
)
def create_backup(
    body: models.CreatePipeline,
    toolmodel: t.Annotated[
        toolmodels_models.DatabaseToolModel,
        fastapi.Depends(toolmodels_injectables.get_existing_capella_model),
    ],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
) -> models.Pipeline:
    git_model = git_injectables.get_existing_git_model(
        body.git_model_id, toolmodel, db
    )
    t4c_model = t4c_injectables.get_existing_t4c_model(
        body.t4c_model_id, toolmodel, db
    )

    username = "techuser-" + str(uuid.uuid4())
    password = credentials.generate_password()

    if not toolmodel.version_id:
        raise toolmodels_exceptions.VersionIdNotSetError(toolmodel.id)

    try:
        t4c_repository_interface.add_user_to_repository(
            t4c_model.repository.instance,
            t4c_model.repository.name,
            username,
            password,
            is_admin=False,
        )
    except requests.RequestException as e:
        log.warning("Pipeline could not be created", exc_info=True)
        raise exceptions.PipelineOperationFailedT4CServerUnreachable(
            exceptions.PipelineOperation.CREATE
        ) from e

    database_pipeline = crud.create_pipeline(
        db=db,
        pipeline=models.DatabasePipeline(
            git_model=git_model,
            t4c_model=t4c_model,
            created_by=username,
            model=toolmodel,
            t4c_username=username,
            t4c_password=password,
            run_nightly=body.run_nightly,
        ),
    )

    if body.run_nightly:
        interface.schedule_pipeline(db, database_pipeline)

    return add_next_run_to_pipeline(
        models.Pipeline.model_validate(database_pipeline)
    )


@router.patch(
    "/{pipeline_id}",
    dependencies=[
        fastapi.Depends(
            projects_permissions_injectables.ProjectPermissionValidation(
                required_scope=projects_permissions_models.ProjectUserScopes(
                    pipelines={permissions_models.UserTokenVerb.UPDATE}
                )
            )
        )
    ],
)
def update_pipeline(
    body: models.UpdatePipeline,
    pipeline: t.Annotated[
        models.DatabasePipeline,
        fastapi.Depends(injectables.get_existing_pipeline),
    ],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
) -> models.Pipeline:
    """Update the trigger configuration of a pipeline."""

    if body.run_nightly and not pipeline.run_nightly:
        interface.schedule_pipeline(db, pipeline)
        pipeline.run_nightly = True
    if not body.run_nightly and pipeline.run_nightly:
        interface.unschedule_pipeline(pipeline)
        pipeline.run_nightly = False

    db.commit()

    return add_next_run_to_pipeline(models.Pipeline.model_validate(pipeline))


@router.delete(
    "/{pipeline_id}",
    status_code=204,
    dependencies=[
        fastapi.Depends(
            projects_permissions_injectables.ProjectPermissionValidation(
                required_scope=projects_permissions_models.ProjectUserScopes(
                    pipelines={permissions_models.UserTokenVerb.DELETE}
                )
            )
        )
    ],
)
def delete_pipeline(
    pipeline: t.Annotated[
        models.DatabasePipeline,
        fastapi.Depends(injectables.get_existing_pipeline),
    ],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
    global_scope: t.Annotated[
        permissions_models.GlobalScopes,
        fastapi.Depends(permissions_injectables.get_scope),
    ],
    force: bool = False,
):
    """Remove a pipeline.

    If the TeamForCapella server is not reachable, the pipeline deletion will fail.
    Users with the `admin.t4c_repositories:update` permission can force the deletion by passing the `force` parameter.
    """

    core.delete_pipeline(db, pipeline, force, global_scope)


router.include_router(
    runs_routes.router,
    prefix="/{pipeline_id}/runs",
)
