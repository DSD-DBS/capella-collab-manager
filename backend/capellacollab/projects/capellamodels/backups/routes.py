# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import json
import logging
import typing as t
import uuid

import fastapi
import requests
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import capellacollab.settings.modelsources.t4c.repositories.interface as t4c_repository_interface
from capellacollab.config import config
from capellacollab.core import credentials
from capellacollab.core.authentication.database import ProjectRoleVerification
from capellacollab.core.database import get_db
from capellacollab.projects.capellamodels.injectables import (
    get_existing_capella_model,
    get_existing_project,
)
from capellacollab.projects.capellamodels.models import DatabaseCapellaModel
from capellacollab.projects.capellamodels.modelsources.git.injectables import (
    get_existing_git_model,
)
from capellacollab.projects.capellamodels.modelsources.t4c.injectables import (
    get_existing_t4c_model,
)
from capellacollab.projects.models import DatabaseProject
from capellacollab.projects.users.models import ProjectUserRole
from capellacollab.sessions.operators import OPERATOR

from . import crud, helper, injectables
from .core import get_environment
from .models import Backup, CreateBackup, DatabaseBackup

router = APIRouter()
log = logging.getLogger(__name__)


@router.get(
    "",
    response_model=t.List[Backup],
    dependencies=[
        Depends(ProjectRoleVerification(required_role=ProjectUserRole.MANAGER))
    ],
)
def get_pipelines(
    model: DatabaseCapellaModel = Depends(get_existing_capella_model),
    db: Session = Depends(get_db),
):
    return [
        helper._inject_last_run(backup)
        for backup in crud.get_pipelines_for_model(db, model)
    ]


@router.post(
    "",
    response_model=Backup,
    dependencies=[
        Depends(ProjectRoleVerification(required_role=ProjectUserRole.MANAGER))
    ],
)
def create_backup(
    body: CreateBackup,
    project: DatabaseProject = Depends(get_existing_project),
    capella_model: DatabaseCapellaModel = Depends(get_existing_capella_model),
    db: Session = Depends(get_db),
):
    gitmodel = get_existing_git_model(body.gitmodel, capella_model, db)
    t4cmodel = get_existing_t4c_model(body.t4cmodel, capella_model, db)

    username = "techuser-" + str(uuid.uuid4())
    password = credentials.generate_password()

    try:
        t4c_repository_interface.add_user_to_repository(
            t4cmodel.repository.instance,
            t4cmodel.repository.name,
            username,
            password,
            is_admin=False,
        )
    except requests.HTTPError:
        raise fastapi.HTTPException(
            500,
            {
                "title": "Creation of the pipeline failed",
                "reason": "We're not able to connect to the TeamForCapella server and therefore cannot prepare the backups. Please try again later or contact your administrator.",
            },
        )

    if body.run_nightly:
        reference = OPERATOR.create_cronjob(
            image="",  # FIXME
            environment=get_environment(
                gitmodel,
                t4cmodel,
                body.include_commit_history,
            ),
            schedule="0 3 * * *",
        )

    return helper._inject_last_run(
        crud.create_pipeline(
            db=db,
            backup=DatabaseBackup(
                project=project.name,
                **body.dict(),
                reference=reference,
                username=username,
            ),
        )
    )


@router.delete(
    "/{pipeline_id}",
    status_code=204,
    dependencies=[
        Depends(ProjectRoleVerification(required_role=ProjectUserRole.MANAGER))
    ],
)
def delete_pipeline(
    pipeline: DatabaseBackup = Depends(injectables.get_existing_pipeline),
    db: Session = Depends(get_db),
):

    try:
        t4c_repository_interface.remove_user_from_repository(
            pipeline.t4c_model.repository.instance,
            pipeline.t4c_model.repository.name,
            pipeline.t4c_username,
        )
    except requests.HTTPError:
        log.error("Error during the deletion of user %s in t4c", exc_info=True)

    OPERATOR.delete_cronjob(pipeline.reference)

    crud.delete_pipeline(db, pipeline)


@router.post(
    "/{pipeline_id}/runs",
    response_model=Backup,
    dependencies=[
        Depends(ProjectRoleVerification(required_role=ProjectUserRole.MANAGER))
    ],
)
def create_job(
    id: int,
    pipeline: DatabaseBackup = Depends(injectables.get_existing_pipeline),
    db: Session = Depends(get_db),
):
    OPERATOR.trigger_cronjob(name=pipeline.reference)


@router.get(
    "/{pipeline_id}/runs/{run_id}/logs",
    response_model=str,
    dependencies=[
        Depends(ProjectRoleVerification(required_role=ProjectUserRole.MANAGER))
    ],
)
def get_logs(
    pipeline_run_id: str = Depends(injectables.get_existing_pipeline_run),
):
    OPERATOR.get_job_logs(id=pipeline_run_id)
    return helper.filter_logs()
