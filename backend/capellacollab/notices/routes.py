# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import typing as t

from fastapi import APIRouter, Depends
from requests import Session

import capellacollab.notices.crud as notices
from capellacollab.core.authentication.database import verify_admin
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.database import get_db
from capellacollab.notices.models import CreateNoticeRequest, NoticeResponse

router = APIRouter()


@router.get(
    "/",
    response_model=t.List[NoticeResponse],
)
def get_notices(db: Session = Depends(get_db)):
    return notices.get_all_notices(db)


@router.get("/{id}")
def get_notice_by_id(id: int, db: Session = Depends(get_db)):
    return notices.get_notice(db, id)


@router.post("/")
def create_notice(
    body: CreateNoticeRequest,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    verify_admin(token, db)
    return notices.create_notice(db, body)


@router.delete(
    "/{id}",
    status_code=204,
)
def delete_notice(
    id: int, db: Session = Depends(get_db), token=Depends(JWTBearer())
):
    verify_admin(token, db)
    notices.delete_notice(db, id)
    return None
