# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from capellacollab.projects.models import DatabaseProject
from capellacollab.projects.users.models import (
    ProjectUserAssociation,
    ProjectUserPermission,
    ProjectUserRole,
)
from capellacollab.users.models import DatabaseUser


def get_users_of_project(db: Session, projects_name: str):
    return (
        db.execute(
            select(ProjectUserAssociation)
            .join(ProjectUserAssociation.project)
            .where(DatabaseProject.name == projects_name)
        )
        .scalars()
        .all()
    )


def get_user_of_project(
    db: Session, project: DatabaseProject, user: DatabaseUser
) -> ProjectUserAssociation:
    return db.execute(
        select(ProjectUserAssociation)
        .where(ProjectUserAssociation.project == project)
        .where(ProjectUserAssociation.user == user)
    ).scalar_one()


def add_user_to_project(
    db: Session,
    project: DatabaseProject,
    user: DatabaseUser,
    role: ProjectUserRole,
    permission: ProjectUserPermission,
) -> ProjectUserAssociation:
    association = ProjectUserAssociation(
        role=role,
        permission=permission,
        project=project,
        user=user,
    )
    db.add(association)
    db.commit()
    return association


def change_role_of_user_in_project(
    db: Session,
    project: DatabaseProject,
    user: DatabaseUser,
    role: ProjectUserRole,
):
    association = db.execute(
        select(ProjectUserAssociation)
        .where(ProjectUserAssociation.project == project)
        .where(ProjectUserAssociation.user == user)
    ).scalar_one()
    association.role = role
    db.commit()
    return association


def change_permission_of_user_in_project(
    db: Session,
    project: DatabaseProject,
    user: DatabaseUser,
    permission: ProjectUserPermission,
) -> ProjectUserAssociation:
    association = db.execute(
        select(ProjectUserAssociation)
        .where(ProjectUserAssociation.project == project)
        .where(ProjectUserAssociation.user == user)
    ).scalar_one()
    association.permission = permission
    db.commit()
    return association


def delete_user_from_project(
    db: Session, project: DatabaseProject, user: DatabaseUser
):
    db.execute(
        delete(ProjectUserAssociation)
        .where(ProjectUserAssociation.user == user)
        .where(ProjectUserAssociation.project == project)
    )
    db.commit()


def delete_users_from_project(db: Session, project: DatabaseProject):
    for association in project.users:
        delete_user_from_project(db, project, association.user)


def delete_projects_for_user(db: Session, user: DatabaseUser):
    db.execute(
        delete(ProjectUserAssociation).where(
            ProjectUserAssociation.user == user
        )
    )
    db.commit()
