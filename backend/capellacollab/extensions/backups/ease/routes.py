# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import logging
import typing as t
import uuid

import requests
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import capellacollab.core.authentication.database as auth
import capellacollab.projects.capellamodels.modelsources.git.crud as git_crud
import capellacollab.projects.capellamodels.modelsources.t4c.connection as t4c_connection
import capellacollab.projects.capellamodels.modelsources.t4c.crud as t4c_crud
from capellacollab.config import config
from capellacollab.core import credentials
from capellacollab.core.authentication.database import ProjectRoleVerification
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.database import get_db
from capellacollab.extensions.backups.ease.models import (
    DB_EASEBackup,
    EASEBackupRequest,
    EASEBackupResponse,
)
from capellacollab.projects.capellamodels.injectables import (
    get_existing_project,
)
from capellacollab.projects.models import DatabaseProject
from capellacollab.projects.users.models import ProjectUserRole
from capellacollab.sessions.operators import OPERATOR

from . import crud, helper

router = APIRouter()
log = logging.getLogger(__name__)

# FIXME: Change usage of id to backup_id (id is reserved)

# FIXME: Change usage of project.name to just project (or project.slug)
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


# FIXME: Change usage of project.name to just project (or project.slug)
@router.post(
    "/",
    response_model=EASEBackupResponse,
)
def create_backup(
    body: EASEBackupRequest,
    project: DatabaseProject = Depends(get_existing_project),
    db: Session = Depends(get_db),
):
    gitmodel = git_crud.get_gitmodel_by_id(db, body.gitmodel)

    # FIXME: Not working
    t4cmodel = t4c_crud.get_t4c_model(db, name, model_id)(
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
        crud.create_backup(
            db=db,
            backup=DB_EASEBackup(
                project=project.name,
                **body.dict(),
                reference=reference,
                username=username,
            ),
        )
    )


# FIXME: Change usage of project.name to just project (or project.slug)
@router.delete(
    "/{id}",
    status_code=204,
    dependencies=[
        Depends(ProjectRoleVerification(required_role=ProjectUserRole.MANAGER))
    ],
)
def delete_backup(
    id: int,
    project: DatabaseProject = Depends(get_existing_project),
    db: Session = Depends(get_db),
):
    backup = crud.get_backup(db, project.name, id)

    # FIXME: Not working
    t4cmodel = t4c_crud.get_project_by_id(
        db=db, id=backup.t4cmodel, repo_name=project.name
    )
    try:
        t4c_connection.remove_user_from_repository(
            t4cmodel.name, backup.username
        )
    except requests.HTTPError:
        log.warning(
            "Error during the deletion of user %s in t4c", exc_info=True
        )

    OPERATOR.delete_cronjob(backup.reference)

    crud.delete_backup(db, project.name, id)
    return None


# FIXME: Change usage of project.name to just project (or project.slug)
@router.post(
    "/{id}/jobs",
    response_model=EASEBackupResponse,
    dependencies=[
        Depends(ProjectRoleVerification(required_role=ProjectUserRole.MANAGER))
    ],
)
def create_job(
    id: int,
    project: DatabaseProject = Depends(get_existing_project),
    db: Session = Depends(get_db),
):
    backup = crud.get_backup(db, project.name, id)
    OPERATOR.trigger_cronjob(name=backup.reference)


# FIXME: Change usage of project to project slug
@router.get(
    "/{bid}/jobs/{jid}/logs",
    response_model=str,
    dependencies=[
        Depends(ProjectRoleVerification(required_role=ProjectUserRole.MANAGER))
    ],
)
def get_logs(
    bid: int,
    jid: str,
):
    # TODO: Check if jid is part of bid

    return OPERATOR.get_job_logs(id=jid)
