# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from __future__ import annotations

import typing as t

from slugify import slugify
from sqlalchemy.orm import Session

from capellacollab.projects.models import DatabaseProject


def get_project_by_name(db: Session, name: str) -> DatabaseProject:
    return (
        db.query(DatabaseProject).filter(DatabaseProject.name == name).first()
    )


def get_project_by_slug(db: Session, slug: str) -> DatabaseProject:
    return (
        db.query(DatabaseProject).filter(DatabaseProject.slug == slug).first()
    )


def get_all_projects(db: Session) -> t.List[DatabaseProject]:
    return db.query(DatabaseProject).all()


def update_description(
    db: Session, project: DatabaseProject, description: str
) -> DatabaseProject:
    project.description = description
    db.commit()
    return project


def create_project(
    db: Session, name: str, description: str | None = None
) -> DatabaseProject:
    repo = DatabaseProject(
        name=name, slug=slugify(name), description=description, users=[]
    )
    db.add(repo)
    db.commit()
    return repo


def delete_project(db: Session, project: DatabaseProject) -> None:
    project.delete()
    db.commit()
