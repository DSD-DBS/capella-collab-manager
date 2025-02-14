# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from collections import abc

import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.permissions import models as permissions_models
from capellacollab.projects import models as projects_models
from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.projects.toolmodels.modelsources.t4c import (
    models as t4c_models,
)
from capellacollab.projects.users import models as projects_users_models
from capellacollab.tools import crud as tools_crud
from capellacollab.tools import models as tools_models
from capellacollab.users import models as users_models

from .. import models as settings_t4c_models
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
    db: orm.Session,
    tool_version: tools_models.DatabaseVersion,
    user: users_models.DatabaseUser,
    global_scope: permissions_models.GlobalScopes,
) -> abc.Sequence[models.DatabaseT4CRepository]:
    tool_versions = [tool_version, *tools_crud.get_compatible_versions_for_tool_versions(db, tool_version=tool_version)]

    if (
        permissions_models.UserTokenVerb.GET
        in global_scope.admin.t4c_repositories
    ):
        return _get_all_matching_t4c_repositories(db, tool_versions)
    return _get_user_write_t4c_repositories(db, tool_versions, user)


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
    db: orm.Session,
    tool_versions: list[tools_models.DatabaseVersion],
    user: users_models.DatabaseUser,
) -> abc.Sequence[models.DatabaseT4CRepository]:
    """Get all T4C repositories for a list of tool_versions and a user"""

    stmt = (
        sa.select(models.DatabaseT4CRepository)
        .join(models.DatabaseT4CRepository.integrations)
        .join(t4c_models.DatabaseT4CModel.model)
        .join(toolmodels_models.DatabaseToolModel.version)
        .where(
            tools_models.DatabaseVersion.id.in_([v.id for v in tool_versions])
        )
        .join(toolmodels_models.DatabaseToolModel.project)
        .where(projects_models.DatabaseProject.is_archived.is_(False))
        .join(projects_models.DatabaseProject.users)
        .where(
            projects_users_models.DatabaseProjectUserAssociation.permission
            == projects_users_models.ProjectUserPermission.WRITE
        )
        .where(
            projects_users_models.DatabaseProjectUserAssociation.user == user
        )
        .distinct()
    )

    return db.execute(stmt).scalars().all()


def _get_all_matching_t4c_repositories(
    db: orm.Session, tool_versions: list[tools_models.DatabaseVersion]
) -> abc.Sequence[models.DatabaseT4CRepository]:
    """Get all T4C repositories for a list of tool_versions"""

    stmt = (
        sa.select(models.DatabaseT4CRepository)
        .join(models.DatabaseT4CRepository.integrations)
        .join(t4c_models.DatabaseT4CModel.model)
        .join(toolmodels_models.DatabaseToolModel.version)
        .where(
            tools_models.DatabaseVersion.id.in_([v.id for v in tool_versions])
        )
        .join(toolmodels_models.DatabaseToolModel.project)
        .where(projects_models.DatabaseProject.is_archived.is_(False))
        .distinct()
    )

    return db.execute(stmt).scalars().all()
