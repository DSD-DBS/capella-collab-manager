# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from fastapi import status
from sqlalchemy import orm

from capellacollab.core import database

from . import crud, models


def get_existing_instance(
    t4c_instance_id: int, db: orm.Session = fastapi.Depends(database.get_db)
) -> models.DatabaseT4CInstance:
    if t4c_instance := crud.get_t4c_instance_by_id(db, t4c_instance_id):
        return t4c_instance

    raise fastapi.HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "reason": f"The t4c instance with the id {t4c_instance_id} does not exist.",
        },
    )
