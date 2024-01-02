# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from sqlalchemy import orm

import capellacollab.notices.crud as notices
from capellacollab.core import database
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.notices.injectables import get_existing_notice
from capellacollab.notices.models import (
    CreateNoticeRequest,
    DatabaseNotice,
    NoticeResponse,
)
from capellacollab.users.models import Role

router = fastapi.APIRouter()


@router.get(
    "",
    response_model=list[NoticeResponse],
)
def get_notices(db: orm.Session = fastapi.Depends(database.get_db)):
    return notices.get_notices(db)


@router.get("/{notice_id}")
def get_notice_by_id(
    notice: DatabaseNotice = fastapi.Depends(get_existing_notice),
):
    return notice


@router.post(
    "",
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(required_role=Role.ADMIN)
        )
    ],
)
def create_notice(
    post_notice: CreateNoticeRequest,
    db: orm.Session = fastapi.Depends(database.get_db),
):
    return notices.create_notice(db, post_notice)


@router.delete(
    "/{notice_id}",
    status_code=204,
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(required_role=Role.ADMIN)
        )
    ],
)
def delete_notice(
    notice: DatabaseNotice = fastapi.Depends(get_existing_notice),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    notices.delete_notice(db, notice)
