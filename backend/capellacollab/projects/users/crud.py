# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import sqlalchemy as sa
from sqlalchemy import exc, orm

from capellacollab.projects import models as projects_models
from capellacollab.projects.users import models
from capellacollab.users import models as users_models


def get_project_user_association_or_raise(
    db: orm.Session,
    project: projects_models.DatabaseProject,
    user: users_models.DatabaseUser,
) -> models.ProjectUserAssociation:
    return db.execute(
        sa.select(models.ProjectUserAssociation)
        .where(models.ProjectUserAssociation.project == project)
        .where(models.ProjectUserAssociation.user == user)
    ).scalar_one()


def get_project_user_association(
    db: orm.Session,
    project: projects_models.DatabaseProject,
    user: users_models.DatabaseUser,
) -> models.ProjectUserAssociation | None:
    try:
        return get_project_user_association_or_raise(db, project, user)
    except exc.NoResultFound:
        return None


def add_user_to_project(
    db: orm.Session,
    project: projects_models.DatabaseProject,
    user: users_models.DatabaseUser,
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
    db: orm.Session,
    project: projects_models.DatabaseProject,
    user: users_models.DatabaseUser,
    role: models.ProjectUserRole,
) -> models.ProjectUserAssociation:
    association = get_project_user_association_or_raise(db, project, user)
    association.role = role
    db.commit()
    return association


def change_permission_of_user_in_project(
    db: orm.Session,
    project: projects_models.DatabaseProject,
    user: users_models.DatabaseUser,
    permission: models.ProjectUserPermission,
) -> models.ProjectUserAssociation:
    association = get_project_user_association_or_raise(db, project, user)
    association.permission = permission
    db.commit()
    return association


def delete_user_from_project(
    db: orm.Session,
    project: projects_models.DatabaseProject,
    user: users_models.DatabaseUser,
):
    db.execute(
        sa.delete(models.ProjectUserAssociation)
        .where(models.ProjectUserAssociation.user == user)
        .where(models.ProjectUserAssociation.project == project)
    )
    db.commit()


def delete_users_from_project(
    db: orm.Session, project: projects_models.DatabaseProject
):
    db.execute(
        sa.delete(models.ProjectUserAssociation).where(
            models.ProjectUserAssociation.project_id == project.id
        )
    )
    db.commit()


def delete_projects_for_user(db: orm.Session, user_id: int):
    db.execute(
        sa.delete(models.ProjectUserAssociation).where(
            models.ProjectUserAssociation.user_id == user_id
        )
    )
    db.commit()
