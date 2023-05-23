# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from __future__ import annotations

import datetime

from sqlalchemy import ARRAY, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

import capellacollab.projects.models as projects_models
import capellacollab.users.models as users_models
from capellacollab.core.database import Base
from capellacollab.sessions.schema import WorkspaceType
from capellacollab.tools.models import Tool, Version


class DatabaseSession(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(primary_key=True, index=True)

    ports: Mapped[list[int]] = mapped_column(ARRAY(Integer))
    created_at: Mapped[datetime.datetime]

    t4c_password: Mapped[str | None]

    rdp_password: Mapped[str | None]
    guacamole_username: Mapped[str | None]
    guacamole_password: Mapped[str | None]
    guacamole_connection_id: Mapped[str | None]

    jupyter_token: Mapped[str | None]

    host: Mapped[str]
    type: Mapped[WorkspaceType]
    mac: Mapped[str]

    owner_name: Mapped[str] = mapped_column(ForeignKey("users.name"))
    owner: Mapped[users_models.DatabaseUser] = relationship()

    tool_id: Mapped[int] = mapped_column(ForeignKey(Tool.id))
    tool: Mapped[Tool] = relationship()

    version_id: Mapped[int] = mapped_column(ForeignKey(Version.id))
    version: Mapped[Version] = relationship()

    project_id: Mapped[str | None] = mapped_column(ForeignKey("projects.id"))
    project: Mapped[projects_models.DatabaseProject] = relationship()
