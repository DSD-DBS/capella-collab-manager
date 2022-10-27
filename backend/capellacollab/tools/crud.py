# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import typing as t

from sqlalchemy import select
from sqlalchemy.orm import Session

from capellacollab.tools.models import (
    CreateTool,
    Nature,
    PatchToolDockerimage,
    Tool,
    Version,
)


def get_all_tools(db: Session) -> t.List[Tool]:
    return db.query(Tool).all()


def get_tool_by_id(id_: int, db: Session) -> Tool:
    return db.execute(select(Tool).where(Tool.id == id_)).scalar_one()


def create_tool(db: Session, tool: Tool) -> Tool:
    db.add(tool)
    db.commit()
    return tool


def update_tool(
    db: Session,
    tool: Tool,
    patch_tool: t.Union[CreateTool, PatchToolDockerimage],
) -> Tool:
    if isinstance(patch_tool, CreateTool):
        tool.name = patch_tool.name
    elif patch_tool.persistent:
        tool.docker_image_template = patch_tool.persistent
        # FIXME: Set readonly image
    db.add(tool)
    db.commit()
    return tool


def delete_tool(db: Session, tool: Tool) -> None:
    db.delete(tool)
    db.commit()


def get_versions(db: Session) -> t.List[Version]:
    return db.query(Version).all()


def get_version_for_tool(
    tool_id: int, version_id: int, db: Session
) -> Version:
    return db.execute(
        select(Version)
        .where(Version.id == version_id)
        .where(Version.tool_id == tool_id)
    ).scalar_one()


def get_version_by_id(id_: int, db: Session) -> Version:
    return db.execute(select(Version).where(Version.id == id_)).scalar_one()


def update_version(version: Version, db: Session) -> Version:
    db.commit()
    return version


def delete_tool_version(version: Version, db: Session) -> None:
    db.delete(version)
    db.commit()


def get_tool_versions(db: Session, tool_id: int) -> t.List[Version]:
    return db.query(Version).filter(Version.tool_id == tool_id).all()


def get_nature_for_tool(tool_id: int, nature_id: int, db: Session) -> Nature:
    return db.execute(
        select(Nature)
        .where(Nature.id == nature_id)
        .where(Nature.tool_id == tool_id)
    ).scalar_one()


def create_version(
    db: Session,
    tool_id: Tool,
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


def get_natures(db: Session) -> t.List[Nature]:
    return db.query(Nature).all()


def get_nature_by_id(id_: int, db: Session) -> Nature:
    return db.execute(select(Nature).where(Nature.id == id_)).scalar_one()


def get_tool_natures(db: Session, tool_id: int) -> t.List[Nature]:
    return db.query(Nature).filter(Nature.tool_id == tool_id).all()


def delete_tool_nature(nature: Nature, db: Session) -> None:
    db.delete(nature)
    db.commit()


def create_nature(db: Session, tool_id: int, name: str) -> Nature:
    nature = Nature(
        name=name,
        tool_id=tool_id,
    )
    db.add(nature)
    db.commit()
    return nature


def get_image_for_tool_version(db: Session, version_id: int) -> str:
    version = get_version_by_id(version_id, db)
    return version.tool.docker_image_template.replace("$version", version.name)


def get_readonly_image_for_version(version: Version):
    return version.tool.readonly_docker_image_template.replace(
        "$version", version.name
    )
