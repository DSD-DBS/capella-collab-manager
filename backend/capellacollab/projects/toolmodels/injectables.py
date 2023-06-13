# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from fastapi import status
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.projects import crud as projects_crud
from capellacollab.projects import models as projects_models

from . import crud, models


def get_existing_project(
    project_slug: str, db: orm.Session = fastapi.Depends(database.get_db)
) -> projects_models.DatabaseProject:
    project = projects_crud.get_project_by_slug(db, project_slug)
    if not project:
        raise fastapi.HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "reason": f"The project having the name {project_slug} was not found.",
                "technical": f"No project with {project_slug} found.",
            },
        )
    return project


def get_existing_capella_model(
    project_slug: str,
    model_slug: str,
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.DatabaseCapellaModel:
    model = crud.get_model_by_slugs(db, project_slug, model_slug)
    if not model:
        raise fastapi.HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "reason": f"The model having the name {model_slug} of the project {project_slug} was not found.",
                "technical": f"No model with {model_slug} found in the project {project_slug}.",
            },
        )
    return model
