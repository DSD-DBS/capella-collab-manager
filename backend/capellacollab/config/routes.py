# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from pydoc import doc
from capellacollab.core.authentication.database import verify_admin
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.database import get_db
from fastapi import APIRouter, Depends
from capellacollab.routes.open_api_configuration import AUTHENTICATION_RESPONSES
from requests import Session


router = APIRouter()

from . import models
from . import crud


@router.put(
    "/dockerimages/environments/{environment}",
    response_model=models.Dockerimages,
    responses=AUTHENTICATION_RESPONSES,
)
def update_dockerimages(
    body: models.Dockerimages,
    environment: str,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    verify_admin(token, db)
    return crud.update_dockerimages_for_environment(db, environment, body).toPydantic()


@router.get(
    "/dockerimages/environments/{environment}",
    response_model=models.Dockerimages,
    responses=AUTHENTICATION_RESPONSES,
)
def get_dockerimages(
    environment: str,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    verify_admin(token, db)
    return crud.get_dockerimages_by_environment(db, environment).toPydantic()
