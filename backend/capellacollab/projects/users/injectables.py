# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from fastapi import status
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.users import crud as users_crud
from capellacollab.users import models as users_models


def get_existing_user(
    user_id: int,
    db: orm.Session = fastapi.Depends(database.get_db),
) -> users_models.DatabaseUser:
    if user := users_crud.get_user_by_id(db, user_id):
        return user

    raise fastapi.HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "err_code": "user_not_exists",
            "reason": f"The user ({user_id}) does not exists",
        },
    )
