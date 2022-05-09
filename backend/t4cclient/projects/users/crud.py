# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

# 3rd party:
from sqlalchemy.orm import Session

# local:
from t4cclient.projects.users.models import (
    ProjectUserAssociation,
    RepositoryUserPermission,
    RepositoryUserRole,
)


def get_users_of_repository(db: Session, repository_name: str):
    return (
        db.query(ProjectUserAssociation)
        .filter(ProjectUserAssociation.repository_name == repository_name)
        .all()
    )


def get_user_of_repository(db: Session, repository_name: str, username: str):
    return (
        db.query(ProjectUserAssociation)
        .filter(ProjectUserAssociation.repository_name == repository_name)
        .filter(ProjectUserAssociation.username == username)
        .first()
    )


def add_user_to_repository(
    db: Session,
    repository_name: str,
    role: RepositoryUserRole,
    username: str,
    permission: RepositoryUserPermission,
):
    association = ProjectUserAssociation(
        repository_name=repository_name,
        username=username,
        role=role,
        permission=permission,
    )
    db.add(association)
    db.commit()
    db.refresh(association)
    return association


def change_role_of_user_in_repository(
    db: Session, repository_name: str, role: RepositoryUserRole, username: str
):
    repo_user = (
        db.query(ProjectUserAssociation)
        .filter(ProjectUserAssociation.repository_name == repository_name)
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
    repository_name: str,
    permission: RepositoryUserPermission,
    username: str,
):
    repo_user = (
        db.query(ProjectUserAssociation)
        .filter(ProjectUserAssociation.repository_name == repository_name)
        .filter(ProjectUserAssociation.username == username)
        .first()
    )
    repo_user.permission = permission
    db.commit()
    db.refresh(repo_user)
    return repo_user


def delete_user_from_repository(db: Session, repository_name: str, username: str):
    db.query(ProjectUserAssociation).filter(
        ProjectUserAssociation.username == username
    ).filter(ProjectUserAssociation.repository_name == repository_name).delete()
    db.commit()


def delete_all_repositories_for_user(db: Session, username: str):
    db.query(ProjectUserAssociation).filter(
        ProjectUserAssociation.username == username
    ).delete()
    db.commit()
