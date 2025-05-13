# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from sqlalchemy import orm

from . import exceptions, injectables, models


def resolve_tags(
    db: orm.Session,
    tag_references: list[str | int] | None,
    scope: models.TagScope,
) -> list[models.DatabaseTag] | None:
    if tag_references is None:
        return None
    tags = []
    for tag in tag_references or []:
        if isinstance(tag, int):
            db_tag = injectables.get_existing_tag_by_id(tag, db)
        else:
            db_tag = injectables.get_existing_tag_by_name(tag, db)

        if db_tag.scope != scope:
            raise exceptions.TagScopeMismatchError(
                db_tag.name,
                actual_tag_scope=scope,
                required_tag_scope=db_tag.scope,
            )
        if db_tag not in tags:
            tags.append(db_tag)
    return tags
