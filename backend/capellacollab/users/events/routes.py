# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from collections import abc

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.users import injectables as users_injectables
from capellacollab.users import models as users_model

from . import crud, models

router = fastapi.APIRouter(
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_model.Role.ADMIN
            )
        )
    ]
)


@router.get("/history/events", response_model=list[models.HistoryEvent])
def get_events(
    db: orm.Session = fastapi.Depends(database.get_db),
) -> abc.Sequence[models.DatabaseUserHistoryEvent]:
    return crud.get_events(db)


@router.get("/{user_id}/history", response_model=models.UserHistory)
def get_user_history(
    user: users_model.DatabaseUser = fastapi.Depends(
        users_injectables.get_existing_user
    ),
) -> users_model.DatabaseUser:
    return user
