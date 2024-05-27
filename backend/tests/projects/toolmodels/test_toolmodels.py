# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from uuid import uuid4

import pytest
from fastapi import testclient
from sqlalchemy import orm

import capellacollab.projects.users.crud as projects_users_crud
import capellacollab.projects.users.models as projects_users_models
from capellacollab.projects import crud as projects_crud
from capellacollab.projects import models as projects_models
from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.users import models as users_models


def test_move_toolmodel(
    project: projects_models.DatabaseProject,
    project_manager: users_models.DatabaseUser,
    capella_model: toolmodels_models.CapellaModel,
    client: testclient.TestClient,
    db: orm.Session,
):
    second_project = projects_crud.create_project(db, str(uuid4()))
    projects_users_crud.add_user_to_project(
        db,
        project=second_project,
        user=project_manager,
        role=projects_users_models.ProjectUserRole.MANAGER,
        permission=projects_users_models.ProjectUserPermission.WRITE,
    )

    response = client.patch(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}",
        json={"project_slug": second_project.slug},
    )
    assert response.status_code == 200

    response = client.get(
        f"/api/v1/projects/{second_project.slug}/models/{capella_model.slug}"
    )
    assert response.status_code == 200


@pytest.mark.usefixtures("project_manager")
def test_move_toolmodel_non_project_member(
    project: projects_models.DatabaseProject,
    capella_model: toolmodels_models.CapellaModel,
    client: testclient.TestClient,
    db: orm.Session,
):
    second_project = projects_crud.create_project(db, str(uuid4()))

    response = client.patch(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}",
        json={"project_slug": second_project.slug},
    )
    assert response.status_code == 403
