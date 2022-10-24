# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


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
        db.query(ProjectUserAssociation)
        .filter(ProjectUserAssociation.projects_name == projects_name)
        .all()
    )


def get_user_of_project(
    db: Session, project: DatabaseProject, user: DatabaseProject
) -> ProjectUserAssociation:
    return (
        db.query(ProjectUserAssociation)
        .filter(ProjectUserAssociation.projects_name == project.name)
        .filter(ProjectUserAssociation.user_id == user.id)
        .first()
    )


def add_user_to_project(
    db: Session,
    project: DatabaseProject,
    user: DatabaseUser,
    role: ProjectUserRole,
    permission: ProjectUserPermission,
) -> ProjectUserAssociation:
    association = ProjectUserAssociation(
        projects_name=project.name,
        user_id=user.id,
        role=role,
        permission=permission,
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
    project_user = (
        db.query(ProjectUserAssociation)
        .filter(ProjectUserAssociation.projects_name == project.name)
        .filter(ProjectUserAssociation.user_id == user.id)
        .first()
    )
    if role == ProjectUserRole.MANAGER:
        project_user.permission = ProjectUserPermission.WRITE
    project_user.role = role
    db.commit()
    return project_user


def change_permission_of_user_in_project(
    db: Session,
    project: DatabaseProject,
    user: DatabaseUser,
    permission: ProjectUserPermission,
) -> ProjectUserAssociation:
    repo_user = (
        db.query(ProjectUserAssociation)
        .filter(ProjectUserAssociation.projects_name == project.name)
        .filter(ProjectUserAssociation.user_id == user.id)
        .first()
    )
    repo_user.permission = permission
    db.commit()
    return repo_user


def delete_user_from_project(
    db: Session, project: DatabaseProject, user: DatabaseUser
):
    db.query(ProjectUserAssociation).filter(
        ProjectUserAssociation.user_id == user.id
    ).filter(ProjectUserAssociation.projects_name == project.name).delete()
    db.commit()


def delete_all_projects_for_user(db: Session, user_id: int):
    db.query(ProjectUserAssociation).filter(
        ProjectUserAssociation.user_id == user_id
    ).delete()
    db.commit()
