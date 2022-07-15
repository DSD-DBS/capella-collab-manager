# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

from fastapi import APIRouter, Depends
from requests import Session

from t4cclient.core.authentication.database import verify_admin
from t4cclient.core.authentication.jwt_bearer import JWTBearer
from t4cclient.core.database import get_db, notices
from t4cclient.core.oauth.responses import AUTHENTICATION_RESPONSES
from t4cclient.schemas.notices import CreateNoticeRequest, NoticeResponse

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


@router.post("/", responses=AUTHENTICATION_RESPONSES)
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
    responses=AUTHENTICATION_RESPONSES,
)
def delete_notice(id: int, db: Session = Depends(get_db), token=Depends(JWTBearer())):
    verify_admin(token, db)
    notices.delete_notice(db, id)
