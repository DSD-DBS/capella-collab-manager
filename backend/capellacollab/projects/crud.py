# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from __future__ import annotations

# Standard library:
import typing as t

from fastapi import HTTPException
from slugify import slugify
from sqlalchemy.orm import Session

from capellacollab.projects.models import DatabaseProject


def get_project(db: Session, name: str) -> DatabaseProject:
    return (
        db.query(DatabaseProject).filter(DatabaseProject.name == name).first()
    )


def get_all_projects(db: Session) -> t.List[DatabaseProject]:
    return db.query(DatabaseProject).all()


def update_description(
    db: Session, name: str, description: str
) -> DatabaseProject:
    project = get_project(db, name)
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
    db.refresh(repo)
    return repo


def delete_project(db: Session, name: str) -> None:
    db.query(DatabaseProject).filter(DatabaseProject.name == name).delete()
    db.commit()


def get_project_by_slug(db: Session, slug: str) -> DatabaseProject:
    project = (
        db.query(DatabaseProject).filter(DatabaseProject.slug == slug).first()
    )
    if not project:
        raise HTTPException(404, "Project not found.")
    return project
