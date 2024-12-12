# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from sqlalchemy import orm

from capellacollab.projects import models as projects_models
from capellacollab.projects.users import crud as projects_users_crud
from capellacollab.projects.users import models as projects_users_models
from capellacollab.users import crud as users_crud
from capellacollab.users import models as users_models


@pytest.fixture(name="project_user_lead")
def fixture_project_user_lead(
    db: orm.Session, project: projects_models.DatabaseProject
) -> projects_users_models.ProjectUserAssociation:
    user = users_crud.create_user(
        db,
        "project_user_lead",
        "project_user_lead",
        None,
        users_models.Role.USER,
    )
    return projects_users_crud.add_user_to_project(
        db,
        project=project,
        user=user,
        role=projects_users_models.ProjectUserRole.MANAGER,
        permission=projects_users_models.ProjectUserPermission.WRITE,
    )


@pytest.fixture(name="project_user_write")
def fixture_project_user_write(
    db: orm.Session, project: projects_models.DatabaseProject
) -> projects_users_models.ProjectUserAssociation:
    user = users_crud.create_user(
        db,
        "project_user_write",
        "project_user_write",
        None,
        users_models.Role.USER,
    )
    return projects_users_crud.add_user_to_project(
        db,
        project=project,
        user=user,
        role=projects_users_models.ProjectUserRole.USER,
        permission=projects_users_models.ProjectUserPermission.WRITE,
    )


@pytest.fixture(name="project_user_read")
def fixture_project_user_read(
    db: orm.Session, project: projects_models.DatabaseProject
) -> projects_users_models.ProjectUserAssociation:
    user = users_crud.create_user(
        db,
        "project_user_read",
        "project_user_read",
        None,
        users_models.Role.USER,
    )
    return projects_users_crud.add_user_to_project(
        db,
        project=project,
        user=user,
        role=projects_users_models.ProjectUserRole.USER,
        permission=projects_users_models.ProjectUserPermission.READ,
    )
