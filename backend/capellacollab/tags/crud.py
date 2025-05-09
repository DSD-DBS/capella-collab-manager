# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from collections import abc

import sqlalchemy as sa
from sqlalchemy import orm

from . import models


def get_all_tags(
    db: orm.Session,
) -> abc.Sequence[models.DatabaseTag]:
    return db.execute(sa.select(models.DatabaseTag)).scalars().all()


def get_tag_by_id(
    db: orm.Session,
    tag_id: int,
) -> models.DatabaseTag | None:
    return db.execute(
        sa.select(models.DatabaseTag).where(models.DatabaseTag.id == tag_id)
    ).scalar_one_or_none()


def get_tag_by_name(
    db: orm.Session,
    tag_name: str,
) -> models.DatabaseTag | None:
    return db.execute(
        sa.select(models.DatabaseTag).where(
            models.DatabaseTag.name == tag_name
        )
    ).scalar_one_or_none()


def create_tag(db: orm.Session, tag: models.CreateTag) -> models.DatabaseTag:
    database_tag = models.DatabaseTag(**tag.model_dump())
    db.add(database_tag)
    db.commit()
    db.refresh(database_tag)
    return database_tag


def update_tag(
    db: orm.Session,
    db_tag: models.DatabaseTag,
    tag: models.CreateTag,
) -> models.DatabaseTag:
    db_tag.name = tag.name
    db_tag.description = tag.description
    db_tag.hex_color = tag.hex_color
    db_tag.icon = tag.icon
    db.commit()
    db.refresh(db_tag)
    return db_tag


def delete_tag(
    db: orm.Session,
    db_tag: models.DatabaseTag,
) -> None:
    db.delete(db_tag)
    db.commit()
