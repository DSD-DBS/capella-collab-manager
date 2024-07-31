# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
import responses
from fastapi import status, testclient
from sqlalchemy import orm

from capellacollab.settings.modelsources.t4c import crud as t4c_crud
from capellacollab.settings.modelsources.t4c import (
    exceptions as settings_t4c_exceptions,
)
from capellacollab.settings.modelsources.t4c import (
    injectables as settings_t4c_injectables,
)
from capellacollab.settings.modelsources.t4c import models as t4c_models
from capellacollab.tools import models as tools_models
from capellacollab.users import crud as users_crud
from capellacollab.users import models as users_models


@pytest.mark.usefixtures("admin")
def test_create_t4c_instance(
    client: testclient.TestClient,
    db: orm.Session,
    tool_version: tools_models.DatabaseVersion,
):
    response = client.post(
        "/api/v1/settings/modelsources/t4c",
        json={
            "license": "test",
            "host": "test",
            "port": 2036,
            "cdo_port": 12036,
            "usage_api": "http://localhost:8086",
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

    t4c_instance = t4c_crud.get_t4c_instance_by_id(db, response.json()["id"])

    assert t4c_instance
    assert t4c_instance.name == "Test integration"


@pytest.mark.usefixtures("admin")
def test_create_t4c_instance_already_existing_name(
    client: testclient.TestClient,
    t4c_instance: t4c_models.DatabaseT4CInstance,
    tool_version: tools_models.DatabaseVersion,
):
    response = client.post(
        "/api/v1/settings/modelsources/t4c",
        json={
            "name": t4c_instance.name,
            "license": "test",
            "host": "test",
            "port": 2036,
            "cdo_port": 12036,
            "usage_api": "http://localhost:8086",
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
        "/api/v1/settings/modelsources/t4c",
    )

    assert len(response.json()) == 2

    assert response.json()[1]["name"] == "test server"

    # Password should not be exposed via API
    assert "password" not in response.json()[1]


def test_get_t4c_instance(
    client: testclient.TestClient,
    db: orm.Session,
    executor_name: str,
    t4c_instance: t4c_models.DatabaseT4CInstance,
):
    users_crud.create_user(
        db, executor_name, executor_name, None, users_models.Role.ADMIN
    )

    response = client.get(
        f"/api/v1/settings/modelsources/t4c/{t4c_instance.id}",
    )

    assert response.json()["name"] == "test server"

    # Password should not be exposed via API
    assert "password" not in response.json()


def test_patch_t4c_instance(
    client: testclient.TestClient,
    db: orm.Session,
    executor_name: str,
    t4c_instance: t4c_models.DatabaseT4CInstance,
):
    users_crud.create_user(
        db, executor_name, executor_name, None, users_models.Role.ADMIN
    )

    response = client.patch(
        f"/api/v1/settings/modelsources/t4c/{t4c_instance.id}",
        json={
            "name": "Patched test integration",
        },
    )

    updated_t4c_instance = t4c_crud.get_t4c_instance_by_id(
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
    t4c_instance: t4c_models.DatabaseT4CInstance,
):
    users_crud.create_user(
        db, executor_name, executor_name, None, users_models.Role.ADMIN
    )

    t4c_crud.update_t4c_instance(
        db, t4c_instance, t4c_models.PatchT4CInstance(is_archived=True)
    )

    response = client.patch(
        f"/api/v1/settings/modelsources/t4c/{t4c_instance.id}",
        json={
            "name": "Patched test integration",
        },
    )

    assert response.status_code == 400


def test_unarchive_t4c_instance(
    client: testclient.TestClient,
    db: orm.Session,
    executor_name: str,
    t4c_instance: t4c_models.DatabaseT4CInstance,
):
    users_crud.create_user(
        db, executor_name, executor_name, None, users_models.Role.ADMIN
    )

    t4c_crud.update_t4c_instance(
        db, t4c_instance, t4c_models.PatchT4CInstance(is_archived=True)
    )

    assert t4c_instance.is_archived

    response = client.patch(
        f"/api/v1/settings/modelsources/t4c/{t4c_instance.id}",
        json={
            "is_archived": False,
        },
    )

    assert response.status_code == 200

    updated_t4c_instance = t4c_crud.get_t4c_instance_by_id(
        db, response.json()["id"]
    )
    assert updated_t4c_instance

    assert not response.json()["is_archived"]
    assert not updated_t4c_instance.is_archived


@pytest.mark.usefixtures("admin")
def test_patch_t4c_instance_already_existing_name(
    client: testclient.TestClient,
    t4c_instance: t4c_models.DatabaseT4CInstance,
    tool_version: tools_models.DatabaseVersion,
):
    instance_name_1 = t4c_instance.name
    instance_name_2 = instance_name_1 + "-2"

    client.post(
        "/api/v1/settings/modelsources/t4c",
        json={
            "name": instance_name_2,
            "license": "test",
            "host": "test",
            "port": 2036,
            "cdo_port": 12036,
            "usage_api": "http://localhost:8086",
            "rest_api": "http://localhost:8080",
            "username": "admin",
            "protocol": "tcp",
            "version_id": tool_version.id,
            "password": "secret-password",
        },
    )

    response = client.patch(
        f"/api/v1/settings/modelsources/t4c/{t4c_instance.id}",
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


def test_injectables_raise_when_archived_instance(
    db: orm.Session,
    executor_name: str,
    t4c_instance: t4c_models.DatabaseT4CInstance,
):
    users_crud.create_user(
        db, executor_name, executor_name, None, users_models.Role.ADMIN
    )

    t4c_crud.update_t4c_instance(
        db, t4c_instance, t4c_models.PatchT4CInstance(is_archived=True)
    )

    with pytest.raises(settings_t4c_exceptions.T4CInstanceIsArchivedError):
        settings_t4c_injectables.get_existing_unarchived_instance(
            t4c_instance.id, db
        )


def test_update_t4c_instance_password_empty_string(
    client: testclient.TestClient,
    db: orm.Session,
    executor_name: str,
    t4c_instance: t4c_models.DatabaseT4CInstance,
):
    users_crud.create_user(
        db, executor_name, executor_name, None, users_models.Role.ADMIN
    )

    expected_password = t4c_instance.password

    response = client.patch(
        f"/api/v1/settings/modelsources/t4c/{t4c_instance.id}",
        json={
            "password": "",
        },
    )

    updated_t4c_instance = t4c_crud.get_t4c_instance_by_id(
        db, response.json()["id"]
    )

    assert updated_t4c_instance
    assert updated_t4c_instance.password == expected_password


@pytest.mark.usefixtures("mock_license_server")
def test_get_t4c_license_usage(
    client: testclient.TestClient,
    db: orm.Session,
    executor_name: str,
    t4c_instance: t4c_models.DatabaseT4CInstance,
):
    users_crud.create_user(
        db, executor_name, executor_name, None, users_models.Role.ADMIN
    )
    response = client.get(
        f"/api/v1/settings/modelsources/t4c/{t4c_instance.id}/licenses",
    )

    assert response.status_code == 200
    assert response.json()["free"] == 19
    assert response.json()["total"] == 20


@responses.activate
def test_get_t4c_license_usage_no_status(
    client: testclient.TestClient,
    db: orm.Session,
    executor_name: str,
    t4c_instance: t4c_models.DatabaseT4CInstance,
):
    users_crud.create_user(
        db, executor_name, executor_name, None, users_models.Role.ADMIN
    )
    responses.get(
        "http://localhost:8086/status/json",
        status=status.HTTP_200_OK,
        json={"status": {"message": "No last status available."}},
    )

    response = client.get(
        f"/api/v1/settings/modelsources/t4c/{t4c_instance.id}/licenses",
    )

    assert response.status_code == 422
    assert (
        response.json()["detail"]["err_code"] == "T4C_LICENSE_SERVER_NO_STATUS"
    )
