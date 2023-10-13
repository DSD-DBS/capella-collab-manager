# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from collections import abc

import slugify
import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.core import database

from . import models


def get_projects(db: orm.Session) -> abc.Sequence[models.DatabaseProject]:
    return db.execute(sa.select(models.DatabaseProject)).scalars().all()


def get_internal_projects(
    db: orm.Session,
) -> abc.Sequence[models.DatabaseProject]:
    return (
        db.execute(
            sa.select(models.DatabaseProject).where(
                models.DatabaseProject.visibility == models.Visibility.INTERNAL
            )
        )
        .scalars()
        .all()
    )


def get_project_by_slug(
    db: orm.Session, slug: str
) -> models.DatabaseProject | None:
    return db.execute(
        sa.select(models.DatabaseProject).where(
            models.DatabaseProject.slug == slug
        )
    ).scalar_one_or_none()


def update_project(
    db: orm.Session,
    project: models.DatabaseProject,
    patch_project: models.PatchProject,
) -> models.DatabaseProject:
    if patch_project.name:
        project.slug = slugify.slugify(patch_project.name)

    database.patch_database_with_pydantic_object(project, patch_project)

    db.commit()
    return project


def create_project(
    db: orm.Session,
    name: str,
    description: str = "",
    visibility: models.Visibility = models.Visibility.PRIVATE,
) -> models.DatabaseProject:
    project = models.DatabaseProject(
        name=name,
        slug=slugify.slugify(name),
        description=description,
        users=[],
        visibility=visibility,
    )

    db.add(project)
    db.commit()
    return project


def delete_project(db: orm.Session, project: models.DatabaseProject) -> None:
    db.delete(project)
    db.commit()
