# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from fastapi import testclient
from sqlalchemy import orm

from capellacollab.projects.toolmodels.modelsources.t4c import (
    crud as models_t4c_crud,
)
from capellacollab.projects.toolmodels.modelsources.t4c import (
    models as models_t4c_models,
)
from capellacollab.settings.modelsources.t4c.instance import (
    crud as t4c_instance_crud,
)
from capellacollab.settings.modelsources.t4c.instance import (
    exceptions as t4c_instance_exceptions,
)
from capellacollab.settings.modelsources.t4c.instance import (
    injectables as t4c_instance_injectables,
)
from capellacollab.settings.modelsources.t4c.instance import (
    models as t4c_instance_models,
)
from capellacollab.settings.modelsources.t4c.license_server import (
    models as t4c_license_server_models,
)
from capellacollab.tools import models as tools_models
from capellacollab.users import crud as users_crud
from capellacollab.users import models as users_models


@pytest.mark.usefixtures("admin")
def test_create_t4c_instance(
    client: testclient.TestClient,
    db: orm.Session,
    tool_version: tools_models.DatabaseVersion,
    t4c_license_server: t4c_license_server_models.DatabaseT4CLicenseServer,
):
    response = client.post(
        "/api/v1/settings/modelsources/t4c/instances",
        json={
            "host": "test",
            "port": 2036,
            "license_server_id": t4c_license_server.id,
            "cdo_port": 12036,
            "rest_api": "http://localhost:8080",
            "username": "admin",
            "protocol": "tcp",
            "name": "Test integration",
            "version_id": tool_version.id,
            "password": "secret-password",
        },
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Test integration"

    t4c_instance = t4c_instance_crud.get_t4c_instance_by_id(
        db, response.json()["id"]
    )

    assert t4c_instance
    assert t4c_instance.name == "Test integration"


@pytest.mark.usefixtures("admin")
def test_create_t4c_instance_already_existing_name(
    client: testclient.TestClient,
    t4c_instance: t4c_instance_models.DatabaseT4CInstance,
    t4c_license_server: t4c_license_server_models.DatabaseT4CLicenseServer,
    tool_version: tools_models.DatabaseVersion,
):
    response = client.post(
        "/api/v1/settings/modelsources/t4c/instances",
        json={
            "name": t4c_instance.name,
            "host": "test",
            "license_server_id": t4c_license_server.id,
            "port": 2036,
            "cdo_port": 12036,
            "rest_api": "http://localhost:8080",
            "username": "admin",
            "protocol": "tcp",
            "version_id": tool_version.id,
            "password": "secret-password",
        },
    )

    assert response.status_code == 409

    detail = response.json()["detail"]

    assert (
        "A T4C Instance with a similar name already exists."
        in detail["reason"]
    )
    assert "name already used" in detail["title"]


@pytest.mark.usefixtures("t4c_instance")
def test_get_t4c_instances(
    client: testclient.TestClient,
    db: orm.Session,
    executor_name: str,
):
    users_crud.create_user(
        db, executor_name, executor_name, None, users_models.Role.ADMIN
    )

    response = client.get(
        "/api/v1/settings/modelsources/t4c/instances",
    )

    assert len(response.json()) == 3
    assert response.json()[-1]["name"] == "test server"

    # Password should not be exposed via API
    assert "password" not in response.json()[1]


def test_get_t4c_instance(
    client: testclient.TestClient,
    db: orm.Session,
    executor_name: str,
    t4c_instance: t4c_instance_models.DatabaseT4CInstance,
):
    users_crud.create_user(
        db, executor_name, executor_name, None, users_models.Role.ADMIN
    )

    response = client.get(
        f"/api/v1/settings/modelsources/t4c/instances/{t4c_instance.id}",
    )

    assert response.json()["name"] == "test server"

    # Password should not be exposed via API
    assert "password" not in response.json()


def test_patch_t4c_instance(
    client: testclient.TestClient,
    db: orm.Session,
    executor_name: str,
    t4c_instance: t4c_instance_models.DatabaseT4CInstance,
):
    users_crud.create_user(
        db, executor_name, executor_name, None, users_models.Role.ADMIN
    )

    response = client.patch(
        f"/api/v1/settings/modelsources/t4c/instances/{t4c_instance.id}",
        json={
            "name": "Patched test integration",
        },
    )

    updated_t4c_instance = t4c_instance_crud.get_t4c_instance_by_id(
        db, response.json()["id"]
    )
    assert updated_t4c_instance

    assert response.status_code == 200

    assert response.json()["name"] == "Patched test integration"
    assert updated_t4c_instance.name == "Patched test integration"

    assert response.json()["host"] == "localhost"
    assert updated_t4c_instance.host == "localhost"


def test_patch_archived_t4c_instance_error(
    client: testclient.TestClient,
    db: orm.Session,
    executor_name: str,
    t4c_instance: t4c_instance_models.DatabaseT4CInstance,
):
    users_crud.create_user(
        db, executor_name, executor_name, None, users_models.Role.ADMIN
    )

    t4c_instance_crud.update_t4c_instance(
        db,
        t4c_instance,
        t4c_instance_models.PatchT4CInstance(is_archived=True),
    )

    response = client.patch(
        f"/api/v1/settings/modelsources/t4c/instances/{t4c_instance.id}",
        json={
            "name": "Patched test integration",
        },
    )

    assert response.status_code == 400


def test_unarchive_t4c_instance(
    client: testclient.TestClient,
    db: orm.Session,
    executor_name: str,
    t4c_instance: t4c_instance_models.DatabaseT4CInstance,
):
    users_crud.create_user(
        db, executor_name, executor_name, None, users_models.Role.ADMIN
    )

    t4c_instance_crud.update_t4c_instance(
        db,
        t4c_instance,
        t4c_instance_models.PatchT4CInstance(is_archived=True),
    )

    assert t4c_instance.is_archived

    response = client.patch(
        f"/api/v1/settings/modelsources/t4c/instances/{t4c_instance.id}",
        json={
            "is_archived": False,
        },
    )

    assert response.status_code == 200

    updated_t4c_instance = t4c_instance_crud.get_t4c_instance_by_id(
        db, response.json()["id"]
    )
    assert updated_t4c_instance

    assert not response.json()["is_archived"]
    assert not updated_t4c_instance.is_archived


@pytest.mark.usefixtures("admin")
def test_patch_t4c_instance_already_existing_name(
    client: testclient.TestClient,
    t4c_instance: t4c_instance_models.DatabaseT4CInstance,
    t4c_license_server: t4c_license_server_models.DatabaseT4CLicenseServer,
    tool_version: tools_models.DatabaseVersion,
):
    instance_name_1 = t4c_instance.name
    instance_name_2 = instance_name_1 + "-2"

    client.post(
        "/api/v1/settings/modelsources/t4c/instances",
        json={
            "name": instance_name_2,
            "host": "test",
            "license_server_id": t4c_license_server.id,
            "port": 2036,
            "cdo_port": 12036,
            "rest_api": "http://localhost:8080",
            "username": "admin",
            "protocol": "tcp",
            "version_id": tool_version.id,
            "password": "secret-password",
        },
    )

    response = client.patch(
        f"/api/v1/settings/modelsources/t4c/instances/{t4c_instance.id}",
        json={
            "name": instance_name_2,
        },
    )

    assert response.status_code == 409

    detail = response.json()["detail"]

    assert (
        "A T4C Instance with a similar name already exists."
        in detail["reason"]
    )
    assert "name already used" in detail["title"]


@pytest.mark.usefixtures("admin")
def test_delete_t4c_instance(
    client: testclient.TestClient,
    db: orm.Session,
    t4c_instance: t4c_instance_models.DatabaseT4CInstance,
    t4c_model: models_t4c_models.DatabaseT4CModel,
):
    response = client.delete(
        f"/api/v1/settings/modelsources/t4c/instances/{t4c_instance.id}",
    )

    assert response.status_code == 204
    assert (
        t4c_instance_crud.get_t4c_instance_by_id(db, t4c_instance.id) is None
    )
    assert models_t4c_crud.get_t4c_model_by_id(db, t4c_model.id) is None


def test_injectables_raise_when_archived_instance(
    db: orm.Session,
    executor_name: str,
    t4c_instance: t4c_instance_models.DatabaseT4CInstance,
):
    users_crud.create_user(
        db, executor_name, executor_name, None, users_models.Role.ADMIN
    )

    t4c_instance_crud.update_t4c_instance(
        db,
        t4c_instance,
        t4c_instance_models.PatchT4CInstance(is_archived=True),
    )

    with pytest.raises(t4c_instance_exceptions.T4CInstanceIsArchivedError):
        t4c_instance_injectables.get_existing_unarchived_instance(
            t4c_instance.id, db
        )


def test_update_t4c_instance_password_empty_string(
    client: testclient.TestClient,
    db: orm.Session,
    executor_name: str,
    t4c_instance: t4c_instance_models.DatabaseT4CInstance,
):
    users_crud.create_user(
        db, executor_name, executor_name, None, users_models.Role.ADMIN
    )

    expected_password = t4c_instance.password

    response = client.patch(
        f"/api/v1/settings/modelsources/t4c/instances/{t4c_instance.id}",
        json={
            "password": "",
        },
    )

    updated_t4c_instance = t4c_instance_crud.get_t4c_instance_by_id(
        db, response.json()["id"]
    )

    assert updated_t4c_instance
    assert updated_t4c_instance.password == expected_password
