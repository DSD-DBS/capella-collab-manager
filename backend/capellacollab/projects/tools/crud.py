# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.projects import models as projects_models
from capellacollab.tools import models as tools_models

from . import models


def create_project_tool(
    db: orm.Session,
    project: projects_models.DatabaseProject,
    tool_version: tools_models.DatabaseVersion,
) -> models.DatabaseProjectToolAssociation:
    project_tool = models.DatabaseProjectToolAssociation(
        project=project, tool_version=tool_version
    )
    db.add(project_tool)
    db.commit()
    db.refresh(project_tool)
    return project_tool


def get_project_tool_by_id(
    db: orm.Session,
    project_tool_id: int,
) -> models.DatabaseProjectToolAssociation | None:
    return db.execute(
        sa.select(models.DatabaseProjectToolAssociation).where(
            models.DatabaseProjectToolAssociation.id == project_tool_id
        )
    ).scalar_one_or_none()


def get_project_tool_by_project_and_tool_version(
    db: orm.Session,
    project: projects_models.DatabaseProject,
    tool_version: tools_models.DatabaseVersion,
) -> models.DatabaseProjectToolAssociation | None:
    return db.execute(
        sa.select(models.DatabaseProjectToolAssociation)
        .where(
            models.DatabaseProjectToolAssociation.tool_version == tool_version
        )
        .where(models.DatabaseProjectToolAssociation.project == project)
    ).scalar_one_or_none()


def delete_project_tool(
    db: orm.Session, project_tool: models.DatabaseProjectToolAssociation
) -> None:
    db.delete(project_tool)
    db.commit()
