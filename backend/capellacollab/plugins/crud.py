# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from collections import abc

import sqlalchemy as sa
from sqlalchemy import orm

from . import models


def get_plugins(db: orm.Session) -> abc.Sequence[models.DatabasePlugin]:
    return db.execute(sa.select(models.DatabasePlugin)).scalars().all()


def get_plugin_by_id(
    db: orm.Session, plugin_id: int
) -> models.DatabasePlugin | None:
    return db.execute(
        sa.select(models.DatabasePlugin).where(
            models.DatabasePlugin.id == plugin_id
        )
    ).scalar_one_or_none()


def create_plugin(
    db: orm.Session,
    remote: str,
    username: str | None,
    password: str | None,
    content: dict | None,
) -> models.DatabasePlugin:
    plugin = models.DatabasePlugin(
        remote=remote, username=username, password=password, content=content
    )
    db.add(plugin)
    db.commit()
    return plugin


def update_plugin(
    db: orm.Session,
    plugin: models.DatabasePlugin,
    patch_plugin: models.PatchPlugin,
    content: str,
) -> models.DatabasePlugin:
    if patch_plugin.username:
        plugin.username = patch_plugin.username
    if patch_plugin.password:
        plugin.password = patch_plugin.password
    if patch_plugin.remote:
        plugin.remote = patch_plugin.remote
    if content:
        plugin.content = content
    db.commit()
    return plugin


def delete_plugin(db: orm.Session, plugin: models.DatabasePlugin) -> None:
    db.delete(plugin)
    db.commit()
