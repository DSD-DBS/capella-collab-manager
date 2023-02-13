# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from capellacollab.core.database import get_db
from capellacollab.sessions.guacamole import get_admin_token
from capellacollab.sessions.operators import get_operator


class StatusResponse(BaseModel):
    guacamole: bool
    database: bool
    operator: bool


router = APIRouter()


@router.get(
    "/status",
    response_model=StatusResponse,
)
def get_status(db: Session = Depends(get_db)):
    return StatusResponse(
        guacamole=validate_guacamole(),
        database=validate_session(db),
        operator=get_operator().validate(),
    )


def validate_guacamole() -> bool:
    try:
        get_admin_token()
        return True
    except BaseException:
        return False


def validate_session(session: Session) -> bool:
    try:
        session.connection()
        return True
    except BaseException:
        return False
