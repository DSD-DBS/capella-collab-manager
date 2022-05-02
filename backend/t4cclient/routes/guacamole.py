# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import json

from fastapi import APIRouter, Depends, HTTPException
from requests import Session
from t4cclient.config import config
from t4cclient.core.authentication.helper import get_username
from t4cclient.core.authentication.jwt_bearer import JWTBearer
from t4cclient.core.database import get_db, sessions
from t4cclient.extensions import guacamole
from t4cclient.routes.open_api_configuration import AUTHENTICATION_RESPONSES
from t4cclient.schemas.guacamole import GuacamoleAuthentication

router = APIRouter()


@router.post(
    "/",
    response_model=GuacamoleAuthentication,
    responses=AUTHENTICATION_RESPONSES,
)
def create_guacamole_token(
    id: str,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    session = sessions.get_session_by_id(db, id)
    if session.owner_name != get_username(token):
        raise HTTPException(
            status_code=403,
            detail="The owner of the session does not match with your username.",
        )

    token = guacamole.get_token(session.guacamole_username, session.guacamole_password)
    return GuacamoleAuthentication(
        token=json.dumps(token),
        url=config["extensions"]["guacamole"]["publicURI"] + "/#/",
    )
