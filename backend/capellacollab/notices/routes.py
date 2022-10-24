# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import typing as t

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import capellacollab.notices.crud as notices
from capellacollab.core.authentication.database import RoleVerification
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.database import get_db
from capellacollab.notices.injectables import get_existing_notice
from capellacollab.notices.models import (
    CreateNoticeRequest,
    DatabaseNotice,
    NoticeResponse,
)
from capellacollab.users.models import Role

router = APIRouter()


@router.get(
    "/",
    response_model=t.List[NoticeResponse],
)
def get_notices(db: Session = Depends(get_db)):
    return notices.get_all_notices(db)


@router.get("/{notice_id}")
def get_notice_by_id(
    notice: DatabaseNotice = Depends(get_existing_notice),
):
    return notice


@router.post(
    "/",
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
)
def create_notice(
    post_notice: CreateNoticeRequest,
    db: Session = Depends(get_db),
):
    return notices.create_notice(db, post_notice)


@router.delete(
    "/{notice_id}",
    status_code=204,
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
)
def delete_notice(
    notice: DatabaseNotice = Depends(get_existing_notice),
    db: Session = Depends(get_db),
):
    notices.delete_notice(db, notice)
    return None
