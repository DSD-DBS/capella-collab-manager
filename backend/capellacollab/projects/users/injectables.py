# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

import capellacollab.users.crud as crud
from capellacollab.core.database import get_db
from capellacollab.users.models import DatabaseUser


def get_existing_user(
    user_id: int,
    db: Session = Depends(get_db),
) -> DatabaseUser:
    if user := crud.get_user_by_id(db, user_id):
        return user

    raise HTTPException(
        status_code=400,
        detail={
            "err_code": "user_not_exists",
            "reason": f"The user ({user_id}) does not exists",
        },
    )
