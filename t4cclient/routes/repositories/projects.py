import typing as t

import t4cclient.core.database as database
import t4cclient.core.database.projects as database_projects
import t4cclient.schemas.repositories.projects as schema_projects
from fastapi import APIRouter, Depends
from requests import Session
from t4cclient.core.oauth.database import verify_admin, verify_repository_role
from t4cclient.core.oauth.jwt_bearer import JWTBearer
from t4cclient.routes.open_api_configuration import AUTHENTICATION_RESPONSES

router = APIRouter()


@router.get(
    "/",
    response_model=t.List[schema_projects.RepositoryProject],
    responses=AUTHENTICATION_RESPONSES,
)
def get_projects_for_repository(
    repository_name: str,
    db: Session = Depends(database.get_db),
    token=Depends(JWTBearer()),
):
    verify_repository_role(
        repository_name, allowed_roles=["manager", "administrator"], token=token, db=db
    )
    db_models = database_projects.get_all_projects(db, repository_name)
    return db_models


@router.post(
    "/",
    response_model=schema_projects.RepositoryProject,
    responses=AUTHENTICATION_RESPONSES,
)
def create_project_in_repository(
    repository_name: str,
    body: schema_projects.RepositoryProjectBase,
    db: Session = Depends(database.get_db),
    token=Depends(JWTBearer()),
):
    verify_repository_role(
        repository_name, allowed_roles=["manager", "administrator"], token=token, db=db
    )
    return database_projects.create_project(db, repository_name, body.name)


@router.delete(
    "/{project_id}",
    status_code=204,
    responses=AUTHENTICATION_RESPONSES,
)
def delete_project_from_repository(
    repository_name: str,
    project_id: int,
    db: Session = Depends(database.get_db),
    token=Depends(JWTBearer()),
):
    verify_admin(token, db)
    return database_projects.delete_project(
        db,
        id=project_id,
        repo_name=repository_name,
    )
