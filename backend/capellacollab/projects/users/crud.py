# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from sqlalchemy import delete, exc, select
from sqlalchemy.orm import Session

from capellacollab.projects.models import DatabaseProject
from capellacollab.projects.users import models
from capellacollab.users.models import DatabaseUser


def get_project_user_association_or_raise(
    db: Session, project: DatabaseProject, user: DatabaseUser
) -> models.ProjectUserAssociation:
    return db.execute(
        select(models.ProjectUserAssociation)
        .where(models.ProjectUserAssociation.project == project)
        .where(models.ProjectUserAssociation.user == user)
    ).scalar_one()


def get_project_user_association(
    db: Session, project: DatabaseProject, user: DatabaseUser
) -> models.ProjectUserAssociation | None:
    try:
        return get_project_user_association_or_raise(db, project, user)
    except exc.NoResultFound:
        return None


def add_user_to_project(
    db: Session,
    project: DatabaseProject,
    user: DatabaseUser,
    role: models.ProjectUserRole,
    permission: models.ProjectUserPermission,
) -> models.ProjectUserAssociation:
    association = models.ProjectUserAssociation(
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
    role: models.ProjectUserRole,
) -> models.ProjectUserAssociation:
    association = get_project_user_association_or_raise(db, project, user)
    association.role = role
    db.commit()
    return association


def change_permission_of_user_in_project(
    db: Session,
    project: DatabaseProject,
    user: DatabaseUser,
    permission: models.ProjectUserPermission,
) -> models.ProjectUserAssociation:
    association = get_project_user_association_or_raise(db, project, user)
    association.permission = permission
    db.commit()
    return association


def delete_user_from_project(
    db: Session, project: DatabaseProject, user: DatabaseUser
):
    db.execute(
        delete(models.ProjectUserAssociation)
        .where(models.ProjectUserAssociation.user == user)
        .where(models.ProjectUserAssociation.project == project)
    )
    db.commit()


def delete_users_from_project(db: Session, project: DatabaseProject):
    db.execute(
        delete(models.ProjectUserAssociation).where(
            models.ProjectUserAssociation.project_id == project.id
        )
    )
    db.commit()


def delete_projects_for_user(db: Session, user_id: int):
    db.execute(
        delete(models.ProjectUserAssociation).where(
            models.ProjectUserAssociation.user_id == user_id
        )
    )
    db.commit()
