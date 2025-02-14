# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t
from collections import abc

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.permissions import injectables as permissions_injectables
from capellacollab.permissions import models as permissions_models

from . import crud, models

router = fastapi.APIRouter()


@router.get(
    "",
    response_model=list[models.HistoryEvent],
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        events={permissions_models.UserTokenVerb.GET}
                    )
                )
            ),
        )
    ],
)
def get_events(
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
) -> abc.Sequence[models.DatabaseUserHistoryEvent]:
    return crud.get_events(db)
