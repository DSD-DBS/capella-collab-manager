# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

# Standard library:
import base64
import typing as t

# 3rd party:
from fastapi import APIRouter, Depends
from requests import Session

# 1st party:
from capellacollab.core.authentication.database import verify_project_role
from capellacollab.core.authentication.database.git_models import (
    verify_gitmodel_permission,
)
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.database import get_db
from capellacollab.extensions.modelsources import git
from capellacollab.extensions.modelsources.git import crud
from capellacollab.sources.git_settings.models import (
    GitSettings,
    GitSettingsGitGetResponse,
    GitType,
)
from capellacollab.routes.open_api_configuration import AUTHENTICATION_RESPONSES

router = APIRouter()


@router.get("/", tags=["git-settings"], responses=AUTHENTICATION_RESPONSES)
def list_git_settings(db: Session = Depends(get_db), token=Depends(JWTBearer())):
    return [
        GitSettingsGitGetResponse(
            id=1,
            type=GitType.GITHUB,
            name="First instance",
            url="https://github.com/machin-bidule",
        ),
        GitSettingsGitGetResponse(
            id=2,
            type=GitType.GITHUB,
            name="Second instance",
            url="https://github.com/truc",
        ),
    ]


@router.get("/{id}", tags=["git-settings"], responses=AUTHENTICATION_RESPONSES)
def get_git_settings(id: int, db: Session = Depends(get_db)):
    return (
        GitSettingsGitGetResponse(
            id=id,
            type=GitType.GITHUB,
            name="Second instance",
            url="https://github.com/truc",
        ),
    )


@router.post("/", tags=["git-settings"], responses=AUTHENTICATION_RESPONSES)
def create_git_settings(body: GitSettings):
    pass


@router.put("/{id}", tags=["git-settings"], responses=AUTHENTICATION_RESPONSES)
def edit_git_settings(id: int, body: GitSettings):
    pass


@router.delete("/{id}", tags=["git-settings"], responses=AUTHENTICATION_RESPONSES)
def delete_git_settings(id: int):
    pass
