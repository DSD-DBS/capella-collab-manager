# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from slugify import slugify
from sqlalchemy.orm import Session

from capellacollab.projects.models import DatabaseProject, PatchProject


def get_project_by_name(db: Session, name: str) -> DatabaseProject:
    return (
        db.query(DatabaseProject).filter(DatabaseProject.name == name).first()
    )


def get_project_by_slug(db: Session, slug: str) -> DatabaseProject:
    return (
        db.query(DatabaseProject).filter(DatabaseProject.slug == slug).first()
    )


def get_all_projects(db: Session) -> list[DatabaseProject]:
    return db.query(DatabaseProject).all()


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
    db: Session, name: str, description: str | None = None
) -> DatabaseProject:
    repo = DatabaseProject(
        name=name, slug=slugify(name), description=description, users=[]
    )
    db.add(repo)
    db.commit()
    return repo


def delete_project(db: Session, project: DatabaseProject) -> None:
    db.delete(project)
    db.commit()
