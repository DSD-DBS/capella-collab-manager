# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from collections import abc

import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.projects import models as projects_models
from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.projects.toolmodels.modelsources.t4c import (
    models as t4c_models,
)
from capellacollab.projects.users import models as projects_users_models
from capellacollab.settings.modelsources.t4c import (
    models as settings_t4c_models,
)
from capellacollab.tools import models as tools_models
from capellacollab.users import models as users_models

from . import models


def get_t4c_repository_by_id(
    db: orm.Session, repo_id: int
) -> models.DatabaseT4CRepository | None:
    return db.execute(
        sa.select(models.DatabaseT4CRepository).where(
            models.DatabaseT4CRepository.id == repo_id
        )
    ).scalar_one_or_none()


def exist_repo_for_name_and_instance(
    db: orm.Session,
    repo_name: str,
    instance: settings_t4c_models.DatabaseT4CInstance,
) -> bool:
    return (
        db.execute(
            sa.select(models.DatabaseT4CRepository)
            .where(models.DatabaseT4CRepository.name == repo_name)
            .where(models.DatabaseT4CRepository.instance_id == instance.id)
        ).scalar_one_or_none()
        is not None
    )


def get_user_t4c_repositories(
    db: orm.Session, version_name: str, user: users_models.DatabaseUser
) -> abc.Sequence[models.DatabaseT4CRepository]:
    if user.role == users_models.Role.ADMIN:
        return _get_admin_t4c_repositories(db, version_name)
    return _get_user_write_t4c_repositories(db, version_name, user)


def create_t4c_repository(
    db: orm.Session,
    repo_name: str,
    instance: settings_t4c_models.DatabaseT4CInstance,
) -> models.DatabaseT4CRepository:
    repository = models.DatabaseT4CRepository(
        name=repo_name, instance=instance
    )

    db.add(repository)
    db.commit()
    return repository


def delete_4c_repository(
    db: orm.Session, repository: models.DatabaseT4CRepository
) -> None:
    db.delete(repository)
    db.commit()


def _get_user_write_t4c_repositories(
    db: orm.Session, version_name: str, user: users_models.DatabaseUser
) -> abc.Sequence[models.DatabaseT4CRepository]:
    stmt = (
        sa.select(models.DatabaseT4CRepository)
        .join(models.DatabaseT4CRepository.models)
        .join(t4c_models.DatabaseT4CModel.model)
        .join(toolmodels_models.DatabaseToolModel.version)
        .where(tools_models.DatabaseVersion.name == version_name)
        .join(toolmodels_models.DatabaseToolModel.project)
        .where(projects_models.DatabaseProject.is_archived.is_(False))
        .join(projects_models.DatabaseProject.users)
        .where(
            projects_users_models.ProjectUserAssociation.permission
            == projects_users_models.ProjectUserPermission.WRITE
        )
        .where(projects_users_models.ProjectUserAssociation.user == user)
    )

    return db.execute(stmt).scalars().all()


def _get_admin_t4c_repositories(
    db: orm.Session, version_name: str
) -> abc.Sequence[models.DatabaseT4CRepository]:
    stmt = (
        sa.select(models.DatabaseT4CRepository)
        .join(models.DatabaseT4CRepository.models)
        .join(t4c_models.DatabaseT4CModel.model)
        .join(toolmodels_models.DatabaseToolModel.version)
        .where(tools_models.DatabaseVersion.name == version_name)
        .join(toolmodels_models.DatabaseToolModel.project)
        .where(projects_models.DatabaseProject.is_archived.is_(False))
    )

    return db.execute(stmt).scalars().all()
