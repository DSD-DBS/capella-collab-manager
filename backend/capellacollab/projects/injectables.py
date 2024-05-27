# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.projects import crud as projects_crud
from capellacollab.projects import models as projects_models

from . import exceptions


def get_existing_project(
    project_slug: str, db: orm.Session = fastapi.Depends(database.get_db)
) -> projects_models.DatabaseProject:
    project = projects_crud.get_project_by_slug(db, project_slug)
    if not project:
        raise exceptions.ProjectNotFoundError(project_slug)
    return project
