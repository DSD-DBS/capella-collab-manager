# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

# Standard library:
import typing as t

# 3rd party:
from fastapi import APIRouter, Depends
from requests import Session

# 1st party:
import capellacollab.core.database as database
import capellacollab.extensions.modelsources.t4c.crud as database_projects
from capellacollab.core.authentication.database import (
    verify_admin,
    verify_project_role,
)
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.routes.open_api_configuration import AUTHENTICATION_RESPONSES

# local:
from . import models as schema_projects

router = APIRouter()


@router.get(
    "/",
    response_model=t.List[schema_projects.RepositoryProject],
    responses=AUTHENTICATION_RESPONSES,
)
def get_t4c_model_for_model(
    project: str,
    db: Session = Depends(database.get_db),
    token=Depends(JWTBearer()),
):
    verify_project_role(
        project, allowed_roles=["manager", "administrator"], token=token, db=db
    )
    db_models = database_projects.get_all_t4c_models(db, project)
    return db_models


@router.post(
    "/",
    response_model=schema_projects.RepositoryProject,
    responses=AUTHENTICATION_RESPONSES,
)
def create_project_in_repository(
    project: str,
    body: schema_projects.RepositoryProjectBase,
    db: Session = Depends(database.get_db),
    token=Depends(JWTBearer()),
):
    verify_project_role(
        project, allowed_roles=["manager", "administrator"], token=token, db=db
    )
    return database_projects.create_project(db, project, body.name)


@router.delete(
    "/{project_id}",
    status_code=204,
    responses=AUTHENTICATION_RESPONSES,
)
def delete_project_from_repository(
    project: str,
    project_id: int,
    db: Session = Depends(database.get_db),
    token=Depends(JWTBearer()),
):
    verify_admin(token, db)
    database_projects.delete_project(
        db,
        id=project_id,
        repo_name=project,
    )
