# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from sqlalchemy import orm

import capellacollab.projects.models as projects_models
import capellacollab.projects.users.crud as projects_users_crud
import capellacollab.projects.users.models as projects_users_models
import capellacollab.users.models as users_models
from capellacollab.projects import models as projects_models
from capellacollab.users import models as users_models


@pytest.fixture
def project_manager(
    db: orm.Session,
    project: projects_models.DatabaseProject,
    user: users_models.DatabaseUser,
) -> users_models.DatabaseUser:
    projects_users_crud.add_user_to_project(
        db,
        project=project,
        user=user,
        role=projects_users_models.ProjectUserRole.MANAGER,
        permission=projects_users_models.ProjectUserPermission.WRITE,
    )
    return user


@pytest.fixture(name="project_user")
def fixture_project_user(
    db: orm.Session,
    project: projects_models.DatabaseProject,
    user: users_models.DatabaseUser,
) -> users_models.DatabaseUser:
    project_user = projects_users_crud.add_user_to_project(
        db,
        project=project,
        user=user,
        role=projects_users_models.ProjectUserRole.USER,
        permission=projects_users_models.ProjectUserPermission.WRITE,
    )
    return project_user
