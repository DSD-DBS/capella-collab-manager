# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

from sqlalchemy.orm import Session

from capellacollab.tools.models import Tool, Type, Version

############
### Tool ###
############


def get_all_tools(db: Session) -> t.List[Tool]:
    return db.query(Tool).all()


def create_tool(db: Session, tool: Tool):
    db.add(tool)
    db.commit()


###############
### Version ###
###############


def get_versions(db: Session) -> t.List[Version]:
    return db.query(Version).all()


def get_tool_versions(db: Session, tool_id: int) -> t.List[Version]:
    return db.query(Version).filter(Version.tool_id == tool_id)


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


############
### Type ###
############


def get_types(db: Session) -> t.List[Type]:
    return db.query(Type).all()


def get_tool_types(db: Session, tool_id: int) -> t.List[Version]:
    return db.query(Version).filter(Version.tool_id == tool_id)


def create_type(db: Session, tool_id: int, model_type: str):
    db.add(
        Type(
            name=model_type,
            tool_id=tool_id,
        )
    )
    db.commit()
