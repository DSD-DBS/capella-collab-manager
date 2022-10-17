# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from capellacollab.core.database import get_db
from capellacollab.sessions.guacamole import get_admin_token
from capellacollab.sessions.operators import OPERATOR


class StatusResponse(BaseModel):
    guacamole: str
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
        database=validate_session(db),
        operator=OPERATOR.validate(),
    )


def validate_guacamole() -> str:
    try:
        get_admin_token()
        return "ok"
    except:
        return "cannot authenticate"


def validate_session(session: Session) -> str:
    try:
        session.connection()
        return "ok"
    except:
        return "no connection"
