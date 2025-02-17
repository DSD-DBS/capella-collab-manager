# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0
import typing as t

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.projects import injectables as projects_injectables
from capellacollab.projects import models as projects_models

from . import crud, exceptions, models


def get_existing_capella_model(
    model_slug: str,
    project: t.Annotated[
        projects_models.DatabaseProject,
        fastapi.Depends(projects_injectables.get_existing_project),
    ],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
) -> models.DatabaseToolModel:
    model = crud.get_model_by_slugs(db, project.slug, model_slug)
    if not model:
        raise exceptions.ToolModelNotFound(project.slug, model_slug)
    return model
