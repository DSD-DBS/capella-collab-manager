# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from sqlalchemy import select

# 3rd party:
from sqlalchemy.orm import Session

from capellacollab.projects.models import DatabaseProject, ProjectWithUsers

# 1st party:
from capellacollab.projects.users.models import (
    ProjectUserAssociation,
    RepositoryUser,
    RepositoryUserPermission,
    RepositoryUserRole,
)
from capellacollab.sql_models.users import DatabaseUser


def get_users_of_repository(db: Session, project_name: str) -> list[RepositoryUser]:
    project = db.execute(
        select(DatabaseProject).filter_by(name=project_name)
    ).scalar_one()
    return ProjectWithUsers.from_orm(project).users


def get_user_of_repository(
    db: Session, projects_name: str, username: str
) -> ProjectUserAssociation:
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
) -> ProjectUserAssociation:
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
) -> ProjectUserAssociation:
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
) -> ProjectUserAssociation:
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


def delete_user_from_repository(db: Session, projects_name: str, username: str) -> None:
    db.query(ProjectUserAssociation).filter(
        ProjectUserAssociation.username == username
    ).filter(ProjectUserAssociation.projects_name == projects_name).delete()
    db.commit()


def delete_all_repositories_for_user(db: Session, username: str) -> None:
    db.query(ProjectUserAssociation).filter(
        ProjectUserAssociation.username == username
    ).delete()
    db.commit()


def stage_project_of_user(
    db: Session, repository_name: str, username: str, staged_by: str
) -> ProjectUserAssociation:
    project_user = get_user_of_repository(db, repository_name, username)
    user = db.execute(select(DatabaseUser).filter_by(name=staged_by)).scalar_one()
    project_user.projects.staged_by = user
    db.commit()
    db.refresh(project_user)
    return project_user


def unstage_project(db: Session, project: DatabaseProject) -> ProjectUserAssociation:
    del project.staged_by
    db.commit()
    print(project)
    return project
