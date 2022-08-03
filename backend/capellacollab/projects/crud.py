# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

# Standard library:
import typing as t

# 3rd party:
from h11 import Data
from slugify import slugify
from sqlalchemy import select
from sqlalchemy.orm import Session

# 1st party:
from capellacollab.projects.models import DatabaseProject


def get_project(db: Session, name: str) -> DatabaseProject:
    return db.query(DatabaseProject).filter(DatabaseProject.name == name).first()


def get_all_projects(db: Session) -> t.List[DatabaseProject]:
    return db.query(DatabaseProject).all()


def update_description(db: Session, name: str, description: str) -> DatabaseProject:
    project = get_project(db, name)
    project.description = description
    db.commit()
    return project


def create_project(db: Session, name: str) -> DatabaseProject:
    slug = slugify(name)
    repo = DatabaseProject(name=name, slug=slug, users=[])
    db.add(repo)
    db.commit()
    db.refresh(repo)
    return repo


def delete_project(db: Session, name: str) -> None:
    db.query(DatabaseProject).filter(DatabaseProject.name == name).delete()
    db.commit()


def get_slug(db: Session, slug: str) -> DatabaseProject:
    project = db.query(DatabaseProject)\
        .filter(DatabaseProject.slug == slug).first()
    assert project is not None
    return project


def get_id(db: Session, id: int):
    return db.query(DatabaseProject).filter(DatabaseProject.id == id).first()
