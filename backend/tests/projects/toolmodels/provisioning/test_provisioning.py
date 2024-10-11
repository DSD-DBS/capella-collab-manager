# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from fastapi import testclient
from sqlalchemy import orm

from capellacollab.projects import models as projects_models
from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.projects.toolmodels.provisioning import (
    crud as provisioning_crud,
)
from capellacollab.projects.toolmodels.provisioning import (
    models as provisioning_models,
)
from capellacollab.users import models as users_models


@pytest.mark.usefixtures("project_user")
def test_get_non_existing_provisioning(
    client: testclient.TestClient,
    project: projects_models.DatabaseProject,
    capella_model: toolmodels_models.DatabaseToolModel,
):
    """Test that a non-existing provisioning returns None"""

    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/provisioning"
    )

    assert response.status_code == 200
    assert response.json() is None


@pytest.mark.usefixtures("project_user")
def test_get_provisioning(
    client: testclient.TestClient,
    project: projects_models.DatabaseProject,
    capella_model: toolmodels_models.DatabaseToolModel,
    provisioning: provisioning_models.DatabaseModelProvisioning,
):
    """Test to get an existing provisioning"""
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/provisioning"
    )

    assert response.status_code == 200

    assert response.json() is not None
    assert response.json()["commit_hash"] == provisioning.commit_hash


@pytest.mark.usefixtures("project_user", "provisioning")
def test_delete_provisioning(
    db: orm.Session,
    user: users_models.DatabaseUser,
    client: testclient.TestClient,
    project: projects_models.DatabaseProject,
    capella_model: toolmodels_models.DatabaseToolModel,
):
    """Test to delete an existing provisioning"""
    response = client.delete(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/provisioning"
    )

    assert response.status_code == 204
    assert (
        provisioning_crud.get_model_provisioning(db, capella_model, user)
        is None
    )


@pytest.mark.usefixtures("project_user")
def test_delete_non_existing_provisioning(
    db: orm.Session,
    user: users_models.DatabaseUser,
    client: testclient.TestClient,
    project: projects_models.DatabaseProject,
    capella_model: toolmodels_models.DatabaseToolModel,
):
    """Test to delete an non-existing provisioning"""

    response = client.delete(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/provisioning"
    )

    assert response.status_code == 404
    assert response.json()["detail"]["err_code"] == "PROVISIONING_NOT_FOUND"
