# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Sequence

from sqlalchemy import exc, select
from sqlalchemy.orm import Session

from capellacollab.core.database import patch_database_with_pydantic_object
from capellacollab.tools.integrations import models as integrations_models
from capellacollab.tools.models import (
    Nature,
    PatchToolDockerimage,
    Tool,
    UpdateToolVersion,
    Version,
)


def get_tools(db: Session) -> Sequence[Tool]:
    return db.execute(select(Tool)).scalars().all()


def get_tool_by_id(db: Session, tool_id: int) -> Tool | None:
    return db.execute(
        select(Tool).where(Tool.id == tool_id)
    ).scalar_one_or_none()


def get_tool_by_name(db: Session, tool_name: str) -> Tool | None:
    return db.execute(
        select(Tool).where(Tool.name == tool_name)
    ).scalar_one_or_none()


def create_tool(db: Session, tool: Tool) -> Tool:
    tool.integrations = integrations_models.DatabaseToolIntegrations(
        pure_variants=False, t4c=False, jupyter=False
    )
    db.add(tool)
    db.commit()
    return tool


def create_tool_with_name(db: Session, tool_name: str) -> Tool:
    return create_tool(db, tool=Tool(name=tool_name, docker_image_template=""))


def update_tool_name(db: Session, tool: Tool, tool_name: str) -> Tool:
    tool.name = tool_name
    db.commit()
    return tool


def update_tool_dockerimages(
    db: Session, tool: Tool, patch_tool: PatchToolDockerimage
) -> Tool:
    if patch_tool.persistent:
        tool.docker_image_template = patch_tool.persistent
    if patch_tool.readonly:
        tool.readonly_docker_image_template = patch_tool.readonly
    if patch_tool.backup:
        tool.docker_image_backup_template = patch_tool.backup
    db.commit()
    return tool


def delete_tool(db: Session, tool: Tool) -> None:
    db.delete(tool)
    db.commit()


def get_versions(db: Session) -> Sequence[Version]:
    return db.execute(select(Version)).scalars().all()


def get_versions_for_tool_id(db: Session, tool_id: int) -> Sequence[Version]:
    return (
        db.execute(select(Version).where(Version.tool_id == tool_id))
        .scalars()
        .all()
    )


def get_version_by_id_or_raise(db: Session, version_id: int) -> Version:
    return db.execute(
        select(Version).where(Version.id == version_id)
    ).scalar_one()


def get_version_by_id(db: Session, version_id: int) -> Version | None:
    try:
        return get_version_by_id_or_raise(db, version_id)
    except exc.NoResultFound:
        return None


def get_version_by_version_and_tool_id(
    db: Session, tool_id: int, version_id: int
) -> Version | None:
    return db.execute(
        select(Version)
        .where(Version.id == version_id)
        .where(Version.tool_id == tool_id)
    ).scalar_one_or_none()


def get_version_by_tool_id_version_name(
    db: Session, tool_id: int, version_name: str
) -> Version | None:
    return db.execute(
        select(Version)
        .where(Version.tool_id == tool_id)
        .where(Version.name == version_name)
    ).scalar_one_or_none()


def update_version(
    db: Session, version: Version, patch_version: UpdateToolVersion
) -> Version:
    patch_database_with_pydantic_object(version, patch_version)

    db.commit()
    return version


def create_version(
    db: Session,
    tool_id: int,
    name: str,
    is_recommended: bool = False,
    is_deprecated: bool = False,
) -> Version:
    version = Version(
        name=name,
        is_recommended=is_recommended,
        is_deprecated=is_deprecated,
        tool_id=tool_id,
    )
    db.add(version)
    db.commit()
    return version


def delete_tool_version(db: Session, version: Version) -> None:
    db.delete(version)
    db.commit()


def get_nature_for_tool(
    db: Session, tool_id: int, nature_id: int
) -> Nature | None:
    return db.execute(
        select(Nature)
        .where(Nature.id == nature_id)
        .where(Nature.tool_id == tool_id)
    ).scalar_one_or_none()


def get_nature_by_name(db: Session, tool: Tool, name: str) -> Nature | None:
    return db.execute(
        select(Nature).where(Nature.tool == tool).where(Nature.name == name)
    ).scalar_one_or_none()


def get_natures(db: Session) -> Sequence[Nature]:
    return db.execute(select(Nature)).scalars().all()


def get_nature_by_id(db: Session, nature_id: int) -> Nature | None:
    return db.execute(
        select(Nature).where(Nature.id == nature_id)
    ).scalar_one_or_none()


def get_natures_by_tool_id(db: Session, tool_id: int) -> Sequence[Nature]:
    return (
        db.execute(select(Nature).where(Nature.tool_id == tool_id))
        .scalars()
        .all()
    )


def create_nature(db: Session, tool_id: int, name: str) -> Nature:
    nature = Nature(name=name, tool_id=tool_id)
    db.add(nature)
    db.commit()
    return nature


def delete_nature(db: Session, nature: Nature) -> None:
    db.delete(nature)
    db.commit()
