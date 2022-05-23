# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

# Standard library:
import typing as t
from os import path

# 3rd party:
import fastapi
from fastapi import APIRouter, Depends
from requests import Session

# 1st party:
import capellacollab.extensions.backups.jenkins.models as jenkins_schema
from capellacollab.core.authentication.database import verify_repository_role
from capellacollab.core.authentication.database.git_models import (
    verify_gitmodel_permission,
)
from capellacollab.core.authentication.database.jenkins import verify_jenkins_permission
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.database import get_db
from capellacollab.extensions.backups import jenkins
from capellacollab.routes.open_api_configuration import AUTHENTICATION_RESPONSES

# local:
from . import crud as jenkins_database

router = APIRouter()


@router.get(
    "/",
    response_model=jenkins_schema.JenkinsPipeline,
    responses=AUTHENTICATION_RESPONSES,
)
def get_jenkins_pipeline(
    repository_name: str,
    model_id: int,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    verify_repository_role(
        repository_name, token=token, db=db, allowed_roles=["manager", "administrator"]
    )
    verify_gitmodel_permission(repository_name, model_id, db)
    db_pipeline = jenkins_database.get_pipeline_of_model(db, model_id)
    if not db_pipeline:
        raise fastapi.HTTPException(
            status_code=404,
            detail="This Git Model has no linked Jenkins Pipeline.",
        )

    latest_run = jenkins.get_pipeline(db, db_pipeline.name)
    pipeline = jenkins_schema.JenkinsPipeline(
        **db_pipeline.__dict__, latest_run=latest_run
    )
    return pipeline


@router.post(
    "/",
    response_model=jenkins_schema.JenkinsPipeline,
    responses=AUTHENTICATION_RESPONSES,
)
def create_jenkins_pipeline(
    repository_name: str,
    model_id: int,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    verify_repository_role(
        repository_name, allowed_roles=["manager", "administrator"], token=token, db=db
    )
    verify_gitmodel_permission(repository_name, model_id, db)
    jenkins.create_pipeline(db, repository_name, model_id)
    pipeline = jenkins_database.add_pipeline(
        db, git_model_id=model_id, name="backup-job-" + str(model_id)
    )
    return pipeline


@router.delete(
    "/{pipeline_name}",
    status_code=204,
    responses=AUTHENTICATION_RESPONSES,
)
def delete_pipeline(
    repository_name: str,
    pipeline_name: str,
    model_id: int,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    verify_repository_role(
        repository_name, allowed_roles=["manager", "administrator"], token=token, db=db
    )
    verify_jenkins_permission(
        repository=repository_name,
        pipeline_name=pipeline_name,
        git_model_id=model_id,
        db=db,
    )
    jenkins.remove_pipeline(pipeline_name)
    jenkins_database.remove_pipeline_by_name(db, pipeline_name)
    return None


@router.post(
    "/{pipeline_name}/jobs",
    status_code=204,
    responses=AUTHENTICATION_RESPONSES,
)
def create_jenkins_job(
    repository_name: str,
    model_id: int,
    pipeline_name: str,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    verify_repository_role(
        repository_name, allowed_roles=["manager", "administrator"], token=token, db=db
    )
    verify_jenkins_permission(
        repository=repository_name,
        pipeline_name=pipeline_name,
        git_model_id=model_id,
        db=db,
    )
    jenkins.trigger_job_run(pipeline_name)
    return None
