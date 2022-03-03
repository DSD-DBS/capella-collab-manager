import typing as t

import t4cclient.core.oauth.database as auth
from fastapi import APIRouter, Depends
from requests import Session
from t4cclient import config, extensions
from t4cclient.core.database import get_db
from t4cclient.core.oauth.jwt_bearer import JWTBearer
from t4cclient.core.operators import OPERATOR
from t4cclient.extensions.modelsources import git, t4c
from t4cclient.routes.open_api_configuration import AUTHENTICATION_RESPONSES

from . import crud, models

router = APIRouter()


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
        project, allowed_roles=["manager", "administrator"], token=token
    )
    return crud.get_backups(db=db, project=project)


@router.get("/{id}")
def get_ease_backup(
    project: str,
    id: int,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    auth.verify_repository_role(
        project, allowed_roles=["manager", "administrator"], token=token
    )
    return crud.get_backup(db=db, project=project, id=id)


@router.post("/", responses=AUTHENTICATION_RESPONSES)
def create_backup(
    project: str,
    body: models.EASEBackupRequest,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    auth.verify_repository_role(
        project, allowed_roles=["manager", "administrator"], token=token
    )

    gitmodel = git.crud.get_model_by_id(
        db=db, repository_name=project, model_id=body.git_model_id
    )

    t4cmodel = t4c.crud.get_project_by_id(
        db=db, id=body.t4c_model_id, repo_name=project
    )

    # Create techuser first

    reference = OPERATOR.create_cronjob(
        image=config.EASE_IMAGE,
        environment={
            "EASE_LOG_LOCATION": "/proc/1/fd/1",
            "GIT_REPO_URL": gitmodel.path,
            "GIT_REPO_BRANCH": gitmodel.revision,
            "T4C_REPO_HOST": config.T4C_SERVER_HOST,
            "T4C_REPO_PORT": config.T4C_SERVER_PORT,
            "T4C_REPO_NAME": project,
            "T4C_PROJECT": t4cmodel.name,
            "T4C_USERNAME": "techuser",
            "T4C_PASSOWRD": "password",
            "GIT_USERNAME": gitmodel.username,
            "GIT_PASSWORD": gitmodel.password,
        },
    )
    return models.DB_EASEBackup(project=project, **body.dict(), reference=reference)


@router.delete(
    "/{id}",
    status_code=204,
    responses=AUTHENTICATION_RESPONSES,
)
def delete_backup(
    project: str, id: int, db: Session = Depends(get_db), token=Depends(JWTBearer())
):
    auth.verify_repository_role(
        project, allowed_roles=["manager", "administrator"], token=token
    )
    # TODO
    pass
