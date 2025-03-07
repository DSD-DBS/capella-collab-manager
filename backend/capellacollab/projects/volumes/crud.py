# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import datetime
import typing as t

import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.projects import models as projects_models

from . import models


def get_all_project_volumes(
    db: orm.Session,
) -> t.Sequence[models.DatabaseProjectVolume]:
    return db.execute(sa.select(models.DatabaseProjectVolume)).scalars().all()


def get_project_volume(
    db: orm.Session, project: projects_models.DatabaseProject
) -> models.DatabaseProjectVolume | None:
    return db.execute(
        sa.select(models.DatabaseProjectVolume).where(
            models.DatabaseProjectVolume.project == project
        )
    ).scalar_one_or_none()


def create_project_volume(
    db: orm.Session,
    project: projects_models.DatabaseProject,
    pvc_name: str,
    size: str,
) -> models.DatabaseProjectVolume:
    database_project_volume = models.DatabaseProjectVolume(
        project=project,
        created_at=datetime.datetime.now(datetime.UTC),
        size=size,
        pvc_name=pvc_name,
    )
    db.add(database_project_volume)
    db.commit()
    return database_project_volume


def delete_project_volume(
    db: orm.Session, project_volume: models.DatabaseProjectVolume
):
    db.delete(project_volume)
    db.commit()
