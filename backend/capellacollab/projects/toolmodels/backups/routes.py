# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import logging
import uuid

import fastapi
import requests
from fastapi import status
from sqlalchemy import orm

import capellacollab.settings.modelsources.t4c.repositories.interface as t4c_repository_interface
from capellacollab.core import credentials, database
from capellacollab.core.authentication import helper as auth_helper
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.core.authentication import jwt_bearer
from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.projects.toolmodels.injectables import (
    get_existing_capella_model,
)
from capellacollab.projects.toolmodels.modelsources.git import (
    injectables as git_injectables,
)
from capellacollab.projects.toolmodels.modelsources.t4c import (
    injectables as t4c_injectables,
)
from capellacollab.projects.users import models as projects_users_models
from capellacollab.sessions import operators
from capellacollab.tools import crud as tools_crud

from . import core, crud, injectables, models
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


@router.get(
    "",
    response_model=list[models.Backup],
)
def get_pipelines(
    model: toolmodels_models.DatabaseCapellaModel = fastapi.Depends(
        get_existing_capella_model
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


@router.post(
    "",
    response_model=models.Backup,
)
def create_backup(
    body: models.CreateBackup,
    capella_model: toolmodels_models.DatabaseCapellaModel = fastapi.Depends(
        get_existing_capella_model
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
    token=fastapi.Depends(jwt_bearer.JWTBearer()),
):
    git_model = git_injectables.get_existing_git_model(
        body.git_model_id, capella_model, db
    )
    t4c_model = t4c_injectables.get_existing_t4c_model(
        body.t4c_model_id, capella_model, db
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
        raise fastapi.HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "err_code": "PIPELINE_CREATION_FAILED_T4C_SERVER_UNREACHABLE",
                "title": "Creation of the pipeline failed",
                "reason": "We're not able to connect to the TeamForCapella server and therefore cannot prepare the backups. Please try again later or contact your administrator.",
            },
        )

    if body.run_nightly:
        reference = operators.get_operator().create_cronjob(
            image=tools_crud.get_backup_image_for_tool_version(
                db, capella_model.version_id
            ),
            environment=core.get_environment(
                git_model,
                t4c_model,
                username,
                password,
                body.include_commit_history,
            ),
            schedule="0 3 * * *",
        )
    else:
        reference = operators.get_operator()._generate_id()

    return crud.create_pipeline(
        db=db,
        pipeline=models.DatabaseBackup(
            k8s_cronjob_id=reference,
            git_model=git_model,
            t4c_model=t4c_model,
            created_by=auth_helper.get_username(token),
            model=capella_model,
            t4c_username=username,
            t4c_password=password,
            include_commit_history=body.include_commit_history,
            run_nightly=body.run_nightly,
        ),
    )


@router.delete(
    "/{pipeline_id}",
    status_code=204,
)
def delete_pipeline(
    pipeline: models.DatabaseBackup = fastapi.Depends(
        injectables.get_existing_pipeline
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    try:
        t4c_repository_interface.remove_user_from_repository(
            pipeline.t4c_model.repository.instance,
            pipeline.t4c_model.repository.name,
            pipeline.t4c_username,
        )
    except requests.RequestException:
        log.error("Error during the deletion of user %s in t4c", exc_info=True)

    if pipeline.run_nightly:
        operators.get_operator().delete_cronjob(pipeline.k8s_cronjob_id)

    crud.delete_pipeline(db, pipeline)


router.include_router(
    runs_routes.router,
    prefix="/{pipeline_id}/runs",
)
