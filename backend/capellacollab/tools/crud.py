# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from collections import abc

import sqlalchemy as sa
from sqlalchemy import exc, orm

from capellacollab.core import database
from capellacollab.tools.integrations import models as integrations_models

from . import exceptions, models


def get_tools(db: orm.Session) -> abc.Sequence[models.DatabaseTool]:
    return db.execute(sa.select(models.DatabaseTool)).scalars().all()


def get_tool_by_id(
    db: orm.Session, tool_id: int
) -> models.DatabaseTool | None:
    return db.execute(
        sa.select(models.DatabaseTool).where(models.DatabaseTool.id == tool_id)
    ).scalar_one_or_none()


def get_tool_by_name(
    db: orm.Session, tool_name: str
) -> models.DatabaseTool | None:
    return db.execute(
        sa.select(models.DatabaseTool).where(
            models.DatabaseTool.name == tool_name
        )
    ).scalar_one_or_none()


def create_tool(
    db: orm.Session, tool: models.DatabaseTool
) -> models.DatabaseTool:
    tool.integrations = integrations_models.DatabaseToolIntegrations(
        pure_variants=False, t4c=False, jupyter=False
    )
    db.add(tool)
    db.commit()
    return tool


def create_tool_with_name(
    db: orm.Session, tool_name: str
) -> models.DatabaseTool:
    return create_tool(
        db, tool=models.DatabaseTool(name=tool_name, docker_image_template="")
    )


def update_tool_name(
    db: orm.Session, tool: models.DatabaseTool, tool_name: str
) -> models.DatabaseTool:
    tool.name = tool_name
    db.commit()
    return tool


def update_tool_dockerimages(
    db: orm.Session,
    tool: models.DatabaseTool,
    patch_tool: models.PatchToolDockerimage,
) -> models.DatabaseTool:
    if patch_tool.persistent:
        tool.docker_image_template = patch_tool.persistent
    if patch_tool.readonly:
        tool.readonly_docker_image_template = patch_tool.readonly
    if patch_tool.backup:
        tool.docker_image_backup_template = patch_tool.backup
    db.commit()
    return tool


def delete_tool(db: orm.Session, tool: models.DatabaseTool) -> None:
    db.delete(tool)
    db.commit()


def get_versions(db: orm.Session) -> abc.Sequence[models.DatabaseVersion]:
    return db.execute(sa.select(models.DatabaseVersion)).scalars().all()


def get_versions_for_tool_id(
    db: orm.Session, tool_id: int
) -> abc.Sequence[models.DatabaseVersion]:
    return (
        db.execute(
            sa.select(models.DatabaseVersion).where(
                models.DatabaseVersion.tool_id == tool_id
            )
        )
        .scalars()
        .all()
    )


def get_version_by_id_or_raise(
    db: orm.Session, version_id: int
) -> models.DatabaseVersion:
    return db.execute(
        sa.select(models.DatabaseVersion).where(
            models.DatabaseVersion.id == version_id
        )
    ).scalar_one()


def get_version_by_id(
    db: orm.Session, version_id: int
) -> models.DatabaseVersion | None:
    try:
        return get_version_by_id_or_raise(db, version_id)
    except exc.NoResultFound:
        return None


def get_version_by_version_and_tool_id(
    db: orm.Session, tool_id: int, version_id: int
) -> models.DatabaseVersion | None:
    return db.execute(
        sa.select(models.DatabaseVersion)
        .where(models.DatabaseVersion.id == version_id)
        .where(models.DatabaseVersion.tool_id == tool_id)
    ).scalar_one_or_none()


def get_version_by_tool_id_version_name(
    db: orm.Session, tool_id: int, version_name: str
) -> models.DatabaseVersion | None:
    return db.execute(
        sa.select(models.DatabaseVersion)
        .where(models.DatabaseVersion.tool_id == tool_id)
        .where(models.DatabaseVersion.name == version_name)
    ).scalar_one_or_none()


def update_version(
    db: orm.Session,
    version: models.DatabaseVersion,
    patch_version: models.UpdateToolVersion,
) -> models.DatabaseVersion:
    database.patch_database_with_pydantic_object(version, patch_version)

    db.commit()
    return version


def create_version(
    db: orm.Session,
    tool_id: int,
    name: str,
    is_recommended: bool = False,
    is_deprecated: bool = False,
) -> models.DatabaseVersion:
    version = models.DatabaseVersion(
        name=name,
        is_recommended=is_recommended,
        is_deprecated=is_deprecated,
        tool_id=tool_id,
    )
    db.add(version)
    db.commit()
    return version


def delete_tool_version(
    db: orm.Session, version: models.DatabaseVersion
) -> None:
    db.delete(version)
    db.commit()


def get_nature_for_tool(
    db: orm.Session, tool_id: int, nature_id: int
) -> models.Nature | None:
    return db.execute(
        sa.select(models.Nature)
        .where(models.Nature.id == nature_id)
        .where(models.Nature.tool_id == tool_id)
    ).scalar_one_or_none()


def get_nature_by_name(
    db: orm.Session, tool: models.DatabaseTool, name: str
) -> models.Nature | None:
    return db.execute(
        sa.select(models.Nature)
        .where(models.Nature.tool == tool)
        .where(models.Nature.name == name)
    ).scalar_one_or_none()


def get_natures(db: orm.Session) -> abc.Sequence[models.Nature]:
    return db.execute(sa.select(models.Nature)).scalars().all()


def get_nature_by_id(db: orm.Session, nature_id: int) -> models.Nature | None:
    return db.execute(
        sa.select(models.Nature).where(models.Nature.id == nature_id)
    ).scalar_one_or_none()


def get_natures_by_tool_id(
    db: orm.Session, tool_id: int
) -> abc.Sequence[models.Nature]:
    return (
        db.execute(
            sa.select(models.Nature).where(models.Nature.tool_id == tool_id)
        )
        .scalars()
        .all()
    )


def create_nature(db: orm.Session, tool_id: int, name: str) -> models.Nature:
    nature = models.Nature(name=name, tool_id=tool_id)
    db.add(nature)
    db.commit()
    return nature


def delete_nature(db: orm.Session, nature: models.Nature) -> None:
    db.delete(nature)
    db.commit()


def get_backup_image_for_tool_version(db: orm.Session, version_id: int) -> str:
    if version := get_version_by_id(db, version_id):
        return version.tool.docker_image_backup_template.replace(
            "$version", version.name
        )

    raise exceptions.ToolVersionNotFoundError(version_id)
