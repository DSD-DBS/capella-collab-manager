# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

import t4cclient.extensions.modelsources.git.crud as git_model_crud
import t4cclient.extensions.modelsources.t4c.connection as t4c_ext
import t4cclient.projects.schemas as repository_schema
import t4cclient.projects.users.models as users_schema
from sqlalchemy.orm.session import Session
from t4cclient.projects.users.models import RepositoryUserPermission


def get_permission(
    repo_permission: RepositoryUserPermission, repository_name: str, db: Session
) -> t.List[RepositoryUserPermission]:
    allowed_permissions: t.List[RepositoryUserPermission] = []

    if git_model_crud.get_primary_model_of_repository(db, repository_name):
        allowed_permissions.append(RepositoryUserPermission.READ)

    if repo_permission == RepositoryUserPermission.WRITE:
        allowed_permissions.append(RepositoryUserPermission.WRITE)
    return allowed_permissions


def get_warnings(
    repository_name: str, db: Session
) -> t.List[repository_schema.Warning]:
    warnings: t.List[repository_schema.Warning] = []
    # if t4c_ext.get_t4c_status()["free"] == 0:
    warnings.append(repository_schema.Warning.LICENCE_LIMIT)

    if not git_model_crud.get_primary_model_of_repository(db, repository_name):
        warnings.append(repository_schema.Warning.NO_GIT_MODEL_DEFINED)
    return warnings
