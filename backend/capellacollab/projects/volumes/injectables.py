# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.projects import injectables as projects_injectables
from capellacollab.projects import models as projects_models

from . import crud, exceptions, models


def get_existing_project_volume(
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
    project: t.Annotated[
        projects_models.DatabaseProject,
        fastapi.Depends(projects_injectables.get_existing_project),
    ],
    project_volume_id: int,
) -> models.DatabaseProjectVolume:
    if volume := crud.get_project_volume(db, project):
        return volume
    raise exceptions.VolumeNotFoundError(project_volume_id, project.slug)
