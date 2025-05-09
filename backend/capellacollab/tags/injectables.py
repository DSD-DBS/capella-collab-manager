# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0
import typing as t

import fastapi
from sqlalchemy import orm

from capellacollab.core import database

from . import crud, exceptions, models


def get_existing_tag_by_id(
    tag_id: int,
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
) -> models.DatabaseTag:
    if tag := crud.get_tag_by_id(db, tag_id):
        return tag
    raise exceptions.TagFoundError(tag_id=tag_id)


def get_existing_tag_by_name(
    tag_name: str,
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
) -> models.DatabaseTag:
    if tag := crud.get_tag_by_name(db, tag_name):
        return tag
    raise exceptions.TagNameFoundError(tag_name=tag_name)
