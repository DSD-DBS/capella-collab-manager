# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from fastapi import status
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.projects import crud as projects_crud
from capellacollab.projects import models as projects_models


def get_existing_project(
    project_slug: str, db: orm.Session = fastapi.Depends(database.get_db)
) -> projects_models.DatabaseProject:
    project = projects_crud.get_project_by_slug(db, project_slug)
    if not project:
        raise fastapi.HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "reason": f"The project with the slug '{project_slug}' was not found.",
                "technical": f"No project with slug '{project_slug}' found.",
            },
        )
    return project
