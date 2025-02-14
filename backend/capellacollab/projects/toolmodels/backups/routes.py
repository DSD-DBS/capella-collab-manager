# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import typing as t
import uuid

import fastapi
import requests
from sqlalchemy import orm

from capellacollab.configuration import core as configuration_core
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
from capellacollab.sessions import operators
from capellacollab.settings.modelsources.t4c.instance.repositories import (
    interface as t4c_repository_interface,
)
from capellacollab.tools import crud as tools_crud

from .. import exceptions as toolmodels_exceptions
from . import core, crud, exceptions, injectables, models
from .runs import routes as runs_routes

router = fastapi.APIRouter()
log = logging.getLogger(__name__)


@router.get(
    "",
    response_model=list[models.Backup],
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
    model: t.Annotated[toolmodels_models.DatabaseToolModel, fastapi.Depends(
        toolmodels_injectables.get_existing_capella_model
    )],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
):
    return crud.get_pipelines_for_tool_model(db, model)


@router.get(
    "/{pipeline_id}",
    response_model=models.Backup,
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
    pipeline: t.Annotated[models.DatabaseBackup, fastapi.Depends(
        injectables.get_existing_pipeline
    )],
):
    return pipeline


@router.post(
    "",
    response_model=models.Backup,
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
    body: models.CreateBackup,
    toolmodel: t.Annotated[toolmodels_models.DatabaseToolModel, fastapi.Depends(
        toolmodels_injectables.get_existing_capella_model
    )],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
):
    git_model = git_injectables.get_existing_git_model(
        body.git_model_id, toolmodel, db
    )
    t4c_model = t4c_injectables.get_existing_t4c_model(
        body.t4c_model_id, toolmodel, db
    )

    username = "techuser-" + str(uuid.uuid4())
    password = credentials.generate_password()

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

    pipeline_config = configuration_core.get_global_configuration(db).pipelines

    if body.run_nightly:
        if not toolmodel.version_id:
            raise toolmodels_exceptions.VersionIdNotSetError(toolmodel.id)

        reference = operators.get_operator().create_cronjob(
            image=tools_crud.get_backup_image_for_tool_version(
                db, toolmodel.version_id
            ),
            environment=core.get_environment(
                git_model,
                t4c_model,
                username,
                password,
                body.include_commit_history,
            ),
            labels=core.get_pipeline_labels(toolmodel),
            tool_resources=toolmodel.tool.config.resources,
            command="backup",
            schedule=pipeline_config.cron,
            timezone=pipeline_config.timezone,
        )
    else:
        reference = operators.get_operator()._generate_id()

    return crud.create_pipeline(
        db=db,
        pipeline=models.DatabaseBackup(
            k8s_cronjob_id=reference,
            git_model=git_model,
            t4c_model=t4c_model,
            created_by=username,
            model=toolmodel,
            t4c_username=username,
            t4c_password=password,
            include_commit_history=body.include_commit_history,
            run_nightly=body.run_nightly,
        ),
    )


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
    pipeline: t.Annotated[models.DatabaseBackup, fastapi.Depends(
        injectables.get_existing_pipeline
    )],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
    global_scope: t.Annotated[permissions_models.GlobalScopes, fastapi.Depends(
        permissions_injectables.get_scope
    )],
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
