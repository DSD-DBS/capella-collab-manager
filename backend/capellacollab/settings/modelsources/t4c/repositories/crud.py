# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

import capellacollab.tools.models as tools_models
from capellacollab.projects.models import DatabaseProject
from capellacollab.projects.toolmodels.models import DatabaseCapellaModel
from capellacollab.projects.toolmodels.modelsources.t4c.models import (
    DatabaseT4CModel,
)
from capellacollab.projects.users import models as projects_users_models
from capellacollab.settings.modelsources.t4c.models import DatabaseT4CInstance
from capellacollab.settings.modelsources.t4c.repositories.models import (
    DatabaseT4CRepository,
)
from capellacollab.users import models as users_models


def get_t4c_repository_by_id(
    db: Session, repo_id: int
) -> DatabaseT4CRepository | None:
    return db.execute(
        select(DatabaseT4CRepository).where(
            DatabaseT4CRepository.id == repo_id
        )
    ).scalar_one_or_none()


def exist_repo_for_name_and_instance(
    db: Session, repo_name: str, instance: DatabaseT4CInstance
) -> bool:
    return (
        db.execute(
            select(DatabaseT4CRepository)
            .where(DatabaseT4CRepository.name == repo_name)
            .where(DatabaseT4CRepository.instance_id == instance.id)
        ).scalar_one_or_none()
        is not None
    )


def get_user_t4c_repositories(
    db: Session, version_name: str, user: users_models.DatabaseUser
) -> Sequence[DatabaseT4CRepository]:
    if user.role == users_models.Role.ADMIN:
        return _get_admin_t4c_repositories(db, version_name)
    return _get_user_write_t4c_repositories(db, version_name, user)


def create_t4c_repository(
    db: Session, repo_name: str, instance: DatabaseT4CInstance
) -> DatabaseT4CRepository:
    repository = DatabaseT4CRepository(name=repo_name, instance=instance)

    db.add(repository)
    db.commit()
    return repository


def delete_4c_repository(
    db: Session, repository: DatabaseT4CRepository
) -> None:
    db.delete(repository)
    db.commit()


def _get_user_write_t4c_repositories(
    db: Session, version_name: str, user: users_models.DatabaseUser
) -> Sequence[DatabaseT4CRepository]:
    stmt = (
        select(DatabaseT4CRepository)
        .join(DatabaseT4CRepository.models)
        .join(DatabaseT4CModel.model)
        .join(DatabaseCapellaModel.version)
        .where(tools_models.Version.name == version_name)
        .join(DatabaseCapellaModel.project)
        .join(DatabaseProject.users)
        .where(
            projects_users_models.ProjectUserAssociation.permission
            == projects_users_models.ProjectUserPermission.WRITE
        )
        .where(projects_users_models.ProjectUserAssociation.user == user)
    )

    return db.execute(stmt).scalars().all()


def _get_admin_t4c_repositories(
    db: Session, version_name: str
) -> Sequence[DatabaseT4CRepository]:
    stmt = (
        select(DatabaseT4CRepository)
        .join(DatabaseT4CRepository.models)
        .join(DatabaseT4CModel.model)
        .join(DatabaseCapellaModel.version)
        .where(tools_models.Version.name == version_name)
    )

    return db.execute(stmt).scalars().all()
