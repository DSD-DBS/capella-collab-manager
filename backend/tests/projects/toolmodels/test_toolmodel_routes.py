# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


from unittest import mock

import pytest
from fastapi import testclient
from sqlalchemy import orm

from capellacollab.__main__ import app
from capellacollab.projects import injectables as projects_injectables
from capellacollab.projects import models as projects_models
from capellacollab.projects.toolmodels import (
    injectables as toolmodels_injectables,
)
from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.users import crud as users_crud
from capellacollab.users import models as users_models


@pytest.fixture(name="override_dependency")
def fixture_override_dependency():
    mock_project = mock.Mock(name="DatabaseProject")

    mock_model = mock.Mock(name="DatabaseModel")
    mock_model.slug = "any-slug"
    mock_model.tool = mock.Mock(name="tool")

    app.dependency_overrides[projects_injectables.get_existing_project] = (
        lambda: mock_project
    )
    app.dependency_overrides[
        toolmodels_injectables.get_existing_capella_model
    ] = lambda: mock_model

    yield

    del app.dependency_overrides[projects_injectables.get_existing_project]
    del app.dependency_overrides[
        toolmodels_injectables.get_existing_capella_model
    ]


def test_rename_toolmodel_successful(
    capella_model: toolmodels_models.DatabaseToolModel,
    project: projects_models.DatabaseProject,
    client: testclient.TestClient,
    executor_name: str,
    db: orm.Session,
):
    users_crud.create_user(db, executor_name, users_models.Role.ADMIN)

    response = client.patch(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}",
        json={
            "name": "new-name",
            "version_id": capella_model.tool.versions[0].id,
            "nature_id": capella_model.tool.natures[0].id,
        },
    )

    assert response.status_code == 200
    assert "new-name" in response.text


@pytest.mark.usefixtures("override_dependency")
def test_rename_toolmodel_where_name_already_exists(
    client: testclient.TestClient,
    executor_name: str,
    db: orm.Session,
):
    users_crud.create_user(db, executor_name, users_models.Role.ADMIN)

    with mock.patch(
        "capellacollab.projects.toolmodels.crud.get_model_by_slugs",
        autospec=True,
    ) as mock_get_model_by_slugs:
        mock_get_model_by_slugs.return_value = "anything"

        response = client.patch(
            "/api/v1/projects/any/models/any",
            json={"name": "new-name", "version_id": -1, "nature_id": -1},
        )

        assert response.status_code == 409
        assert "A model with a similar name already exists" in response.text
        mock_get_model_by_slugs.assert_called_once()


def test_update_toolmodel_order_successful(
    capella_model: toolmodels_models.DatabaseToolModel,
    project: projects_models.DatabaseProject,
    client: testclient.TestClient,
    executor_name: str,
    db: orm.Session,
):
    users_crud.create_user(db, executor_name, users_models.Role.ADMIN)

    response = client.patch(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}",
        json={"display_order": 1},
    )

    assert response.status_code == 200
    assert "1" in response.text
