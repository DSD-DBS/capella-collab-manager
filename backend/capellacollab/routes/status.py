# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import fastapi
import pydantic
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.sessions import guacamole, operators


class StatusResponse(pydantic.BaseModel):
    guacamole: bool
    database: bool
    operator: bool


router = fastapi.APIRouter()


@router.get("/status", response_model=StatusResponse)
def get_status(db: orm.Session = fastapi.Depends(database.get_db)):
    return StatusResponse(
        guacamole=validate_guacamole(),
        database=validate_session(db),
        operator=operators.get_operator().validate(),
    )


def validate_guacamole() -> bool:
    try:
        guacamole.get_admin_token()
        return True
    except BaseException:
        return False


def validate_session(db: orm.Session) -> bool:
    try:
        db.connection()
        return True
    except BaseException:
        return False
