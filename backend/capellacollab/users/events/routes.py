# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.core.database import get_db
from capellacollab.users.events.models import (
    DatabaseUserHistoryEvent,
    HistoryEvent,
    UserHistory,
)
from capellacollab.users.injectables import get_existing_user
from capellacollab.users.models import DatabaseUser, Role

from . import crud

router = APIRouter(
    dependencies=[
        Depends(auth_injectables.RoleVerification(required_role=Role.ADMIN))
    ]
)


@router.get("/history/events", response_model=list[HistoryEvent])
def get_events(
    db: Session = Depends(get_db),
) -> list[DatabaseUserHistoryEvent]:
    return crud.get_events(db)


@router.get("/{user_id}/history/", response_model=UserHistory)
def get_user_history(
    user: DatabaseUser = Depends(get_existing_user),
) -> DatabaseUser:
    return user
