# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from sqlalchemy import orm

import capellacollab.notices.crud as notices
from capellacollab.core import database
from capellacollab.notices.injectables import get_existing_notice
from capellacollab.notices.models import (
    CreateNoticeRequest,
    DatabaseNotice,
    NoticeResponse,
)
from capellacollab.permissions import injectables as permissions_injectables
from capellacollab.permissions import models as permissions_models

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
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        announcements={permissions_models.UserTokenVerb.CREATE}
                    )
                )
            ),
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
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        announcements={permissions_models.UserTokenVerb.DELETE}
                    )
                )
            ),
        )
    ],
)
def delete_notice(
    notice: DatabaseNotice = fastapi.Depends(get_existing_notice),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    notices.delete_notice(db, notice)
