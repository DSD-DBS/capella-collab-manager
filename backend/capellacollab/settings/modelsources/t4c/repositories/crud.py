# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from capellacollab.projects.models import DatabaseProject
from capellacollab.projects.toolmodels.models import DatabaseCapellaModel
from capellacollab.projects.toolmodels.modelsources.t4c.models import (
    DatabaseT4CModel,
)
from capellacollab.projects.users.models import (
    ProjectUserAssociation,
    ProjectUserPermission,
)
from capellacollab.settings.modelsources.t4c.models import DatabaseT4CInstance
from capellacollab.settings.modelsources.t4c.repositories.models import (
    CreateT4CRepository,
    DatabaseT4CRepository,
)
from capellacollab.users.models import DatabaseUser, Role


def get_t4c_repository(id_: int, db: Session) -> DatabaseT4CRepository:
    return db.execute(
        select(DatabaseT4CRepository).where(DatabaseT4CRepository.id == id_)
    ).scalar_one()


def create_t4c_repository(
    repository: CreateT4CRepository, instance: DatabaseT4CInstance, db: Session
):
    repository = DatabaseT4CRepository(name=repository.name)
    repository.instance = instance
    db.add(repository)
    db.commit()
    db.refresh(repository)
    return repository


def delete_4c_repository(
    repository: DatabaseT4CRepository, db: Session
) -> None:
    db.delete(repository)
    db.commit()


def get_user_t4c_repositories(
    db: Session, version_name: str, user: DatabaseUser
) -> list[DatabaseT4CRepository]:
    admin_stmt = (
        select(DatabaseT4CRepository)
        .join(DatabaseT4CRepository.models)
        .join(DatabaseT4CModel.model)
        .join(DatabaseCapellaModel.version)
        .where(Version.name == version_name)
    )

    stmt = (
        admin_stmt.join(DatabaseCapellaModel.project)
        .join(DatabaseProject.users)
        .where(
            ProjectUserAssociation.permission == ProjectUserPermission.WRITE
        )
        .where(ProjectUserAssociation.user == user)
    )

    return (
        db.execute(admin_stmt if user.role == Role.ADMIN else stmt)
        .scalars()
        .all()
    )
