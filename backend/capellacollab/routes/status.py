# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

# 3rd party:
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

# 1st party:
from capellacollab.core.database import get_db
from capellacollab.extensions.modelsources.t4c.connection import get_t4c_status
from capellacollab.sessions.guacamole import get_admin_token
from capellacollab.sessions.operators import OPERATOR


class StatusResponse(BaseModel):
    guacamole: str
    license_server: str
    database: str
    operator: str


router = APIRouter()


@router.get(
    "/status",
    response_model=StatusResponse,
)
def get_status(db: Session = Depends(get_db)):
    return StatusResponse(
        guacamole=validate_guacamole(),
        license_server=validate_license_server(),
        database=validate_session(db),
        operator=OPERATOR.validate(),
    )


def validate_guacamole() -> str:
    try:
        get_admin_token()
        return "ok"
    except:
        return "cannot authenticate"


def validate_license_server() -> str:
    try:
        get_t4c_status()
        return "ok"
    except:
        return "cannot reach license server"


def validate_session(session: Session) -> str:
    try:
        session.connection()
        return "ok"
    except:
        return "no connection"
