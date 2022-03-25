import logging
import typing as t
import uuid

import requests
import t4cclient.core.authentication.database as auth
from fastapi import APIRouter, Depends
from requests import Session
from t4cclient import config, extensions
from t4cclient.core import credentials
from t4cclient.core.authentication.jwt_bearer import JWTBearer
from t4cclient.core.database import get_db
from t4cclient.core.operators import OPERATOR
from t4cclient.extensions.modelsources import git, t4c
from t4cclient.routes.open_api_configuration import AUTHENTICATION_RESPONSES

from . import crud, helper, models

router = APIRouter()
log = logging.getLogger(__name__)


@router.get(
    "/",
    response_model=t.List[models.EASEBackupResponse],
    responses=AUTHENTICATION_RESPONSES,
)
def get_ease_backups(
    project: str,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    auth.verify_repository_role(
        project, allowed_roles=["manager", "administrator"], token=token, db=db
    )
    return [
        helper._inject_last_run(backup)
        for backup in crud.get_backups(db=db, project=project)
    ]


@router.post(
    "/", response_model=models.EASEBackupResponse, responses=AUTHENTICATION_RESPONSES
)
def create_backup(
    project: str,
    body: models.EASEBackupRequest,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    auth.verify_repository_role(
        project, allowed_roles=["manager", "administrator"], token=token, db=db
    )

    gitmodel = git.crud.get_model_by_id(
        db=db, repository_name=project, model_id=body.gitmodel
    )

    t4cmodel = t4c.crud.get_project_by_id(db=db, id=body.t4cmodel, repo_name=project)

    username = "techuser-" + str(uuid.uuid4())
    password = credentials.generate_password()
    t4c.connection.add_user_to_repository(project, username, password)

    reference = OPERATOR.create_cronjob(
        image=config.IMPORTER_IMAGE,
        environment={
            "EASE_LOG_LOCATION": "/proc/1/fd/1",
            "GIT_REPO_URL": gitmodel.path,
            "GIT_REPO_BRANCH": gitmodel.revision,
            "T4C_REPO_HOST": config.T4C_SERVER_HOST,
            "T4C_REPO_PORT": config.T4C_SERVER_PORT,
            "T4C_REPO_NAME": project,
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
            backup=models.DB_EASEBackup(
                project=project, **body.dict(), reference=reference, username=username
            ),
        )
    )


@router.delete(
    "/{id}",
    status_code=204,
    responses=AUTHENTICATION_RESPONSES,
)
def delete_backup(
    project: str, id: int, db: Session = Depends(get_db), token=Depends(JWTBearer())
):
    auth.verify_repository_role(
        project, allowed_roles=["manager", "administrator"], token=token, db=db
    )

    backup = crud.get_backup(db, project, id)
    t4cmodel = t4c.crud.get_project_by_id(db=db, id=backup.t4cmodel, repo_name=project)
    try:
        t4c.connection.remove_user_from_repository(t4cmodel.name, backup.username)
    except requests.HTTPError:
        log.warning("Error during the deletion of user %s in t4c", exc_info=True)

    OPERATOR.delete_cronjob(backup.reference)

    crud.delete_backup(db, project, id)
    return None


@router.post(
    "/{id}/jobs",
    response_model=models.EASEBackupResponse,
    responses=AUTHENTICATION_RESPONSES,
)
def create_job(
    project: str,
    id: int,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    auth.verify_repository_role(
        project, allowed_roles=["manager", "administrator"], token=token, db=db
    )

    backup = crud.get_backup(db=db, project=project, id=id)

    OPERATOR.trigger_cronjob(name=backup.reference)


@router.get(
    "/{bid}/jobs/{jid}/logs",
    response_model=str,
    responses=AUTHENTICATION_RESPONSES,
)
def get_logs(
    project: str,
    bid: int,
    jid: str,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    auth.verify_repository_role(
        project, allowed_roles=["manager", "administrator"], token=token, db=db
    )
    # TODO: Check if jid is part of bid

    return OPERATOR.get_job_logs(id=jid)
