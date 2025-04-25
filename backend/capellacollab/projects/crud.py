# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from collections import abc

import slugify
import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.projects.users import models as project_users_models
from capellacollab.users import models as users_models

from . import models


def get_projects(db: orm.Session) -> abc.Sequence[models.DatabaseProject]:
    return db.execute(sa.select(models.DatabaseProject)).scalars().all()


def get_internal_projects(
    db: orm.Session,
) -> abc.Sequence[models.DatabaseProject]:
    return (
        db.execute(
            sa.select(models.DatabaseProject).where(
                models.DatabaseProject.visibility
                == models.ProjectVisibility.INTERNAL
            )
        )
        .scalars()
        .all()
    )


def get_project_by_name(
    db: orm.Session, name: str
) -> models.DatabaseProject | None:
    return db.execute(
        sa.select(models.DatabaseProject).where(
            models.DatabaseProject.name == name
        )
    ).scalar_one_or_none()


def get_project_by_slug(
    db: orm.Session, slug: str
) -> models.DatabaseProject | None:
    return db.execute(
        sa.select(models.DatabaseProject).where(
            models.DatabaseProject.slug == slug
        )
    ).scalar_one_or_none()


def get_common_projects_for_users(
    db: orm.Session,
    user1: users_models.DatabaseUser,
    user2: users_models.DatabaseUser,
) -> abc.Sequence[models.DatabaseProject]:
    user1_table = orm.aliased(
        project_users_models.DatabaseProjectUserAssociation
    )
    user2_table = orm.aliased(
        project_users_models.DatabaseProjectUserAssociation
    )

    return (
        db.execute(
            sa.select(models.DatabaseProject)
            .join(
                user1_table,
                models.DatabaseProject.id == user1_table.project_id,
            )
            .join(
                user2_table,
                models.DatabaseProject.id == user2_table.project_id,
            )
            .where(user1_table.user_id == user1.id)
            .where(user2_table.user_id == user2.id)
            .distinct()
        )
        .scalars()
        .all()
    )


def update_project(
    db: orm.Session,
    project: models.DatabaseProject,
    patch_project: models.PatchProject,
) -> models.DatabaseProject:
    database.patch_database_with_pydantic_object(project, patch_project)

    db.commit()
    return project


def create_project(
    db: orm.Session,
    name: str,
    description: str = "",
    visibility: models.ProjectVisibility = models.ProjectVisibility.PRIVATE,
    type: models.ProjectType = models.ProjectType.GENERAL,
) -> models.DatabaseProject:
    project = models.DatabaseProject(
        name=name,
        slug=slugify.slugify(name),
        description=description,
        users=[],
        visibility=visibility,
        type=type,
    )

    db.add(project)
    db.commit()
    return project


def delete_project(db: orm.Session, project: models.DatabaseProject) -> None:
    db.delete(project)
    db.commit()
