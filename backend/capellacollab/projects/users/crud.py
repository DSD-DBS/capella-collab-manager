# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from sqlalchemy.orm import Session

from capellacollab.projects.users.models import (
    ProjectUserAssociation,
    RepositoryUserPermission,
    RepositoryUserRole,
)


def get_users_of_repository(db: Session, projects_name: str):
    return (
        db.query(ProjectUserAssociation)
        .filter(ProjectUserAssociation.projects_name == projects_name)
        .all()
    )


def get_user_of_repository(db: Session, projects_name: str, username: str):
    return (
        db.query(ProjectUserAssociation)
        .filter(ProjectUserAssociation.projects_name == projects_name)
        .filter(ProjectUserAssociation.username == username)
        .first()
    )


def add_user_to_repository(
    db: Session,
    projects_name: str,
    role: RepositoryUserRole,
    username: str,
    permission: RepositoryUserPermission,
):
    association = ProjectUserAssociation(
        projects_name=projects_name,
        username=username,
        role=role,
        permission=permission,
    )
    db.add(association)
    db.commit()
    db.refresh(association)
    return association


def change_role_of_user_in_repository(
    db: Session, projects_name: str, role: RepositoryUserRole, username: str
):
    repo_user = (
        db.query(ProjectUserAssociation)
        .filter(ProjectUserAssociation.projects_name == projects_name)
        .filter(ProjectUserAssociation.username == username)
        .first()
    )
    if role == RepositoryUserRole.MANAGER:
        repo_user.permission = RepositoryUserPermission.WRITE
    repo_user.role = role
    db.commit()
    db.refresh(repo_user)
    return repo_user


def change_permission_of_user_in_repository(
    db: Session,
    projects_name: str,
    permission: RepositoryUserPermission,
    username: str,
):
    repo_user = (
        db.query(ProjectUserAssociation)
        .filter(ProjectUserAssociation.projects_name == projects_name)
        .filter(ProjectUserAssociation.username == username)
        .first()
    )
    repo_user.permission = permission
    db.commit()
    db.refresh(repo_user)
    return repo_user


def delete_user_from_repository(
    db: Session, projects_name: str, username: str
):
    db.query(ProjectUserAssociation).filter(
        ProjectUserAssociation.username == username
    ).filter(ProjectUserAssociation.projects_name == projects_name).delete()
    db.commit()


def delete_all_repositories_for_user(db: Session, username: str):
    db.query(ProjectUserAssociation).filter(
        ProjectUserAssociation.username == username
    ).delete()
    db.commit()
