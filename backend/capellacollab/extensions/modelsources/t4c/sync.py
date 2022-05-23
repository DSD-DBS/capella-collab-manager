# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

# Standard library:
import typing as t

# 3rd party:
from fastapi import APIRouter, Depends
from requests import Session

# 1st party:
import capellacollab.extensions.modelsources.t4c.connection as t4c_manager
from capellacollab.core.authentication import database as database_auth
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.database import get_db, projects
from capellacollab.routes.open_api_configuration import AUTHENTICATION_RESPONSES

router = APIRouter()


@router.post(
    "/repositories",
    status_code=204,
    tags=["Repositories"],
    responses=AUTHENTICATION_RESPONSES,
)
def fetch_repositories_from_t4c(
    db: Session = Depends(get_db), token=Depends(JWTBearer())
):
    database_auth.verify_admin(token, db)

    t4c_server_repos = t4c_manager.get_repositories()
    repos = [repo.name for repo in projects.get_all_repositories(db=db)]

    difference = list(set(t4c_server_repos) - set(repos))

    for repo in difference:
        projects.create_repository(db=db, name=repo)
