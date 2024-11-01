# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import logging
import uuid

import fastapi
import requests
from sqlalchemy import orm

from capellacollab.core import credentials, database
from capellacollab.core.authentication import injectables as auth_injectables
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
from capellacollab.projects.users import models as projects_users_models
from capellacollab.sessions import operators
from capellacollab.settings.configuration import core as configuration_core
from capellacollab.settings.modelsources.t4c.instance.repositories import (
    interface as t4c_repository_interface,
)
from capellacollab.tools import crud as tools_crud

from .. import exceptions as toolmodels_exceptions
from . import core, crud, exceptions, injectables, models
from .runs import routes as runs_routes

router = fastapi.APIRouter(
    dependencies=[
        fastapi.Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=projects_users_models.ProjectUserRole.MANAGER
            )
        )
    ]
)
log = logging.getLogger(__name__)


@router.get("", response_model=list[models.Backup])
def get_pipelines(
    model: toolmodels_models.DatabaseToolModel = fastapi.Depends(
        toolmodels_injectables.get_existing_capella_model
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    return crud.get_pipelines_for_tool_model(db, model)


@router.get(
    "/{pipeline_id}",
    response_model=models.Backup,
)
def get_pipeline(
    pipeline: models.DatabaseBackup = fastapi.Depends(
        injectables.get_existing_pipeline
    ),
):
    return pipeline


@router.post("", response_model=models.Backup)
def create_backup(
    body: models.CreateBackup,
    toolmodel: toolmodels_models.DatabaseToolModel = fastapi.Depends(
        toolmodels_injectables.get_existing_capella_model
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
    username: str = fastapi.Depends(auth_injectables.get_username),
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
    except requests.RequestException:
        log.warning("Pipeline could not be created", exc_info=True)
        raise exceptions.PipelineOperationFailedT4CServerUnreachable(
            exceptions.PipelineOperation.CREATE
        )

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


@router.delete("/{pipeline_id}", status_code=204)
def delete_pipeline(
    pipeline: models.DatabaseBackup = fastapi.Depends(
        injectables.get_existing_pipeline
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
    username: str = fastapi.Depends(auth_injectables.get_username),
    force: bool = False,
):
    core.delete_pipeline(db, pipeline, username, force)


router.include_router(
    runs_routes.router,
    prefix="/{pipeline_id}/runs",
)
