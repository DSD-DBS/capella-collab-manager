# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from capellacollab.core.database import get_db
from capellacollab.projects import crud as projects_crud
from capellacollab.projects.models import DatabaseProject

from . import crud
from .models import DatabaseCapellaModel


def get_existing_project(
    project_slug: str, db: Session = Depends(get_db)
) -> DatabaseProject:
    project = projects_crud.get_project_by_slug(db, project_slug)
    if not project:
        raise HTTPException(
            404,
            {
                "reason": f"The project having the name {project_slug} was not found.",
                "technical": f"No project with {project_slug} found.",
            },
        )
    return project


def get_existing_capella_model(
    project_slug: str, model_slug: str, db: Session = Depends(get_db)
) -> DatabaseCapellaModel:
    model = crud.get_model_by_slugs(db, project_slug, model_slug)
    if not model:
        raise HTTPException(
            404,
            {
                "reason": f"The model having the name {model_slug} of the project {project_slug} was not found.",
                "technical": f"No model with {model_slug} found in the project {project_slug}.",
            },
        )
    return model
