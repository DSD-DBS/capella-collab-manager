# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.permissions import injectables as permissions_injectables
from capellacollab.permissions import models as permissions_models

from . import crud, injectables, models

router = fastapi.APIRouter()


@router.get(
    "",
    response_model=list[models.AnnouncementResponse],
)
def get_announcements(
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
):
    return crud.get_announcements(db)


@router.get("/{announcement_id}")
def get_announcement_by_id(
    announcement: t.Annotated[
        models.DatabaseAnnouncement,
        fastapi.Depends(injectables.get_existing_announcement),
    ],
):
    return announcement


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
def create_announcement(
    post_announcement: models.CreateAnnouncementRequest,
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
):
    return crud.create_announcement(db, post_announcement)


@router.patch(
    "/{announcement_id}",
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        announcements={permissions_models.UserTokenVerb.UPDATE}
                    )
                )
            ),
        )
    ],
)
def update_announcement(
    post_announcement: models.CreateAnnouncementRequest,
    announcement: t.Annotated[
        models.DatabaseAnnouncement,
        fastapi.Depends(injectables.get_existing_announcement),
    ],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
):
    return crud.update_announcement(db, announcement, post_announcement)


@router.delete(
    "/{announcement_id}",
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
def delete_announcement(
    announcement: t.Annotated[
        models.DatabaseAnnouncement,
        fastapi.Depends(injectables.get_existing_announcement),
    ],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
):
    crud.delete_announcement(db, announcement)
