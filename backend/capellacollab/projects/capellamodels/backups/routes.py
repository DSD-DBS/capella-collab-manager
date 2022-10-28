# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import logging
import typing as t
import uuid

import requests
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import capellacollab.projects.capellamodels.modelsources.t4c.connection as t4c_connection
from capellacollab.config import config
from capellacollab.core import credentials
from capellacollab.core.authentication.database import ProjectRoleVerification
from capellacollab.core.database import get_db
from capellacollab.projects.capellamodels.injectables import (
    get_existing_capella_model,
    get_existing_project,
)
from capellacollab.projects.capellamodels.modelsources.git.injectables import (
    get_existing_git_model,
)
from capellacollab.projects.models import DatabaseProject
from capellacollab.projects.users.models import ProjectUserRole
from capellacollab.sessions.operators import OPERATOR

from . import crud, helper, injectables
from .models import DB_EASEBackup, EASEBackupRequest, EASEBackupResponse

router = APIRouter()
log = logging.getLogger(__name__)


@router.get(
    "/",
    response_model=t.List[EASEBackupResponse],
    dependencies=[
        Depends(ProjectRoleVerification(required_role=ProjectUserRole.MANAGER))
    ],
)
def get_ease_backups(
    project: DatabaseProject = Depends(get_existing_project),
    db: Session = Depends(get_db),
):
    return [
        helper._inject_last_run(backup)
        for backup in crud.get_backups(db, project.name)
    ]


@router.post(
    "/",
    response_model=EASEBackupResponse,
)
def create_backup(
    body: EASEBackupRequest,
    project: DatabaseProject = Depends(get_existing_project),
    capella_model=Depends(get_existing_capella_model),
    db: Session = Depends(get_db),
):
    gitmodel = get_existing_git_model(body.gitmodel, capella_model, db)
    t4cmodel = get_existing_t4c_model(body.t4cmodel, capella_model, db)(
        db=db, id=body.t4cmodel, repo_name=project.name
    )

    username = "techuser-" + str(uuid.uuid4())
    password = credentials.generate_password()
    t4c_connection.add_user_to_repository(
        project.name, username, password, is_admin=False
    )

    reference = OPERATOR.create_cronjob(
        image=config["docker"]["images"]["backup"],
        environment={
            "EASE_LOG_LOCATION": "/proc/1/fd/1",
            "GIT_REPO_URL": gitmodel.path,
            "GIT_REPO_BRANCH": gitmodel.revision,
            "T4C_REPO_HOST": config["modelsources"]["t4c"]["host"],
            "T4C_REPO_PORT": config["modelsources"]["t4c"]["port"],
            "T4C_CDO_PORT": config["modelsources"]["t4c"]["cdoPort"],
            "T4C_REPO_NAME": project.name,
            "T4C_PROJECT_NAME": t4cmodel.name,
            "T4C_USERNAME": username,
            "T4C_PASSWORD": password,
            "GIT_USERNAME": gitmodel.username,
            "GIT_PASSWORD": gitmodel.password,
        },
        schedule="0 3 * * *",
    )

    return helper._inject_last_run(
        crud.create_pipeline(
            db=db,
            backup=DB_EASEBackup(
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
    pipeline: DB_EASEBackup = Depends(injectables.get_existing_pipeline),
    db: Session = Depends(get_db),
):

    try:
        t4c_connection.remove_user_from_repository(
            pipeline.t4c_model.repository.name, pipeline.t4c_username
        )
    except requests.HTTPError:
        log.error("Error during the deletion of user %s in t4c", exc_info=True)

    OPERATOR.delete_cronjob(pipeline.reference)

    crud.delete_pipeline(db, pipeline)


@router.post(
    "/{pipeline_id}/runs",
    response_model=EASEBackupResponse,
    dependencies=[
        Depends(ProjectRoleVerification(required_role=ProjectUserRole.MANAGER))
    ],
)
def create_job(
    id: int,
    pipeline: DB_EASEBackup = Depends(injectables.get_existing_pipeline),
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
