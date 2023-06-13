# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from fastapi import status
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.notices import crud, models


def get_existing_notice(
    notice_id: int,
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.DatabaseNotice:
    if notice := crud.get_notice_by_id(db, notice_id):
        return notice

    raise fastapi.HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={
            "err_code": "notice_not_exists",
            "reason": f"The notice ({notice_id}) does not exists",
        },
    )
