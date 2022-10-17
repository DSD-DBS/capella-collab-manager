# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import typing as t

from sqlalchemy import select
from sqlalchemy.orm import Session

from capellacollab.tools.models import (
    CreateTool,
    PatchToolDockerimage,
    Tool,
    Type,
    Version,
)


def get_all_tools(db: Session) -> t.List[Tool]:
    return db.query(Tool).all()


def get_tool_by_id(id_: int, db: Session) -> Tool:
    return db.execute(select(Tool).where(Tool.id == id_)).scalar_one()


def create_tool(db: Session, tool: Tool):
    db.add(tool)
    db.commit()


def update_tool(
    db: Session,
    tool: Tool,
    patch_tool: t.Union[CreateTool, PatchToolDockerimage],
):
    if isinstance(patch_tool, CreateTool):
        tool.name = patch_tool.name
    else:
        if patch_tool.persistent:
            tool.docker_image_template = patch_tool.persistent
            # FIXME: Set readonly image
    db.add(tool)
    db.commit()
    return tool


def delete_tool(db: Session, tool: Tool):
    db.delete(tool)
    db.commit()


def get_versions(db: Session) -> t.List[Version]:
    return db.query(Version).all()


def get_version_by_id(id_: int, db: Session) -> Version:
    return db.execute(select(Version).where(Version.id == id_)).scalar_one()


def get_tool_versions(db: Session, tool_id: int) -> t.List[Version]:
    return db.query(Version).filter(Version.tool_id == tool_id).all()


def create_version(
    db: Session,
    tool_id: Tool,
    model_version: str,
    is_recommended: bool = False,
    is_deprecated: bool = False,
):
    db.add(
        Version(
            name=model_version,
            is_recommended=is_recommended,
            is_deprecated=is_deprecated,
            tool_id=tool_id,
        )
    )
    db.commit()


def get_types(db: Session) -> t.List[Type]:
    return db.query(Type).all()


def get_type_by_id(id_: int, db: Session) -> Type:
    return db.execute(select(Type).where(Type.id == id_)).scalar_one()


def get_tool_types(db: Session, tool_id: int) -> t.List[Type]:
    return db.query(Type).filter(Type.tool_id == tool_id).all()


def create_type(db: Session, tool_id: int, model_type: str):
    db.add(
        Type(
            name=model_type,
            tool_id=tool_id,
        )
    )
    db.commit()


def get_image_for_tool_version(db: Session, version_id: int):
    version = get_version_by_id(version_id, db)
    return version.tool.docker_image_template.replace("$version", version.name)
