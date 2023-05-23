# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Sequence

from slugify import slugify
from sqlalchemy import select
from sqlalchemy.orm import Session

from capellacollab.projects.models import DatabaseProject, PatchProject


def get_projects(db: Session) -> Sequence[DatabaseProject]:
    return db.execute(select(DatabaseProject)).scalars().all()


def get_project_by_slug(db: Session, slug: str) -> DatabaseProject | None:
    return db.execute(
        select(DatabaseProject).where(DatabaseProject.slug == slug)
    ).scalar_one_or_none()


def update_project(
    db: Session, project: DatabaseProject, patch_project: PatchProject
) -> DatabaseProject:
    if patch_project.name:
        project.name = patch_project.name
        project.slug = slugify(patch_project.name)
    if patch_project.description:
        project.description = patch_project.description
    db.commit()
    return project


def create_project(
    db: Session, name: str, description: str = ""
) -> DatabaseProject:
    project = DatabaseProject(
        name=name, slug=slugify(name), description=description, users=[]
    )

    db.add(project)
    db.commit()
    return project


def delete_project(db: Session, project: DatabaseProject) -> None:
    db.delete(project)
    db.commit()
