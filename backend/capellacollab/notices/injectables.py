# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from capellacollab.core.database import get_db
from capellacollab.notices import crud
from capellacollab.notices.models import DatabaseNotice


def get_existing_notice(
    notice_id: int,
    db: Session = Depends(get_db),
) -> DatabaseNotice:
    if notice := crud.get_notice_by_id(db, notice_id):
        return notice

    raise HTTPException(
        status_code=400,
        detail={
            "err_code": "notice_not_exists",
            "reason": f"The notice ({notice_id}) does not exists",
        },
    )
