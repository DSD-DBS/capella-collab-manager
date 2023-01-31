# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from __future__ import annotations

import datetime
import typing as t

import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.core.database import Base
from capellacollab.sessions.schema import WorkspaceType
from capellacollab.tools.models import Tool, Version

if t.TYPE_CHECKING:
    import capellacollab.projects.models as projects_models
    import capellacollab.users.models as users_models


class DatabaseSession(Base):
    __tablename__ = "sessions"

    id: str = sa.Column(sa.String, primary_key=True, index=True)
    owner_name: str = sa.Column(sa.String, sa.ForeignKey("users.name"))
    owner: users_models.DatabaseUser = orm.relationship("DatabaseUser")
    tool_id: int = sa.Column(sa.Integer, sa.ForeignKey(Tool.id))
    tool: Tool = orm.relationship(Tool)

    version_id: int = sa.Column(sa.Integer, sa.ForeignKey(Version.id))
    version: Version = orm.relationship(Version)
    ports: list[int] = sa.Column(sa.ARRAY(sa.Integer))
    created_at: datetime.datetime = sa.Column(sa.TIMESTAMP)
    t4c_password: str = sa.Column(sa.String, nullable=True)
    rdp_password: str = sa.Column(sa.String)
    guacamole_username: str = sa.Column(sa.String)
    guacamole_password: str = sa.Column(sa.String)
    guacamole_connection_id: str = sa.Column(sa.String)
    host: str = sa.Column(sa.String)
    type: WorkspaceType = sa.Column(sa.Enum(WorkspaceType), nullable=False)
    project_id: str = sa.Column(
        sa.Integer, sa.ForeignKey("projects.id"), nullable=True
    )
    project: projects_models.DatabaseProject = orm.relationship(
        "DatabaseProject"
    )
    mac: str = sa.Column(sa.String)
