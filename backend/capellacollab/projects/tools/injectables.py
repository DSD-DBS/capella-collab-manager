# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0
import typing as t

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.projects import injectables as projects_injectables
from capellacollab.projects import models as projects_models

from . import crud, exceptions, models


def get_existing_project_tool(
    project_tool_id: int,
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
    project: t.Annotated[projects_models.DatabaseProject, fastapi.Depends(
        projects_injectables.get_existing_project
    )],
) -> models.DatabaseProjectToolAssociation:
    project_tool = crud.get_project_tool_by_id(db, project_tool_id)
    if not project_tool:
        raise exceptions.ProjectToolNotFound(project_tool_id)
    if project_tool.project != project:
        raise exceptions.ProjectToolBelongsToOtherProject(
            project_tool_id, project.slug
        )
    return project_tool
