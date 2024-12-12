# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
import responses
from fastapi import status, testclient
from sqlalchemy import orm

from capellacollab.settings.modelsources.t4c.license_server import (
    crud as license_server_crud,
)
from capellacollab.settings.modelsources.t4c.license_server import (
    models as license_server_models,
)
from capellacollab.users import crud as users_crud
from capellacollab.users import models as users_models


@pytest.mark.usefixtures("admin")
def test_create_t4c_license_server(
    client: testclient.TestClient,
    db: orm.Session,
):
    response = client.post(
        "/api/v1/settings/modelsources/t4c/license-servers",
        json={
            "name": "test",
            "usage_api": "http://localhost:8086",
            "license_key": "test_license_key",
        },
    )

    assert response.status_code == 200
    assert response.json()["name"] == "test"

    t4c_instance = license_server_crud.get_t4c_license_server_by_id(
        db, response.json()["id"]
    )

    assert t4c_instance
    assert t4c_instance.name == "test"


@pytest.mark.usefixtures("admin")
def test_create_t4c_license_server_already_existing_name(
    client: testclient.TestClient,
    t4c_license_server: license_server_models.DatabaseT4CLicenseServer,
):
    response = client.post(
        "/api/v1/settings/modelsources/t4c/license-servers",
        json={
            "name": t4c_license_server.name,
            "usage_api": "http://localhost:8086",
            "license_key": "test_license_key",
        },
    )

    assert response.status_code == 409

    assert (
        response.json()["detail"]["err_code"] == "RESOURCE_NAME_ALREADY_IN_USE"
    )


@pytest.mark.usefixtures("t4c_license_server")
def test_get_t4c_license_servers_admin(
    client: testclient.TestClient,
    db: orm.Session,
    executor_name: str,
):
    users_crud.create_user(
        db, executor_name, executor_name, None, users_models.Role.ADMIN
    )

    response = client.get(
        "/api/v1/settings/modelsources/t4c/license-servers",
    )

    assert len(response.json()) == 3

    assert response.json()[-1]["name"] == "test license server"
    assert response.json()[-1]["license_key"] == "test key"
    assert response.json()[-1]["usage_api"] == "http://localhost:8086"


@pytest.mark.usefixtures("t4c_license_server")
def test_get_t4c_license_servers(
    client: testclient.TestClient,
    db: orm.Session,
    executor_name: str,
):
    """Test that the license server data is anonymized without permissions"""

    users_crud.create_user(
        db, executor_name, executor_name, None, users_models.Role.USER
    )

    response = client.get(
        "/api/v1/settings/modelsources/t4c/license-servers",
    )

    assert len(response.json()) == 3

    assert response.json()[-1]["name"] == "test license server"
    assert response.json()[-1]["license_key"] == ""
    assert response.json()[-1]["usage_api"] == ""


def test_get_t4c_license_server(
    client: testclient.TestClient,
    db: orm.Session,
    executor_name: str,
    t4c_license_server: license_server_models.DatabaseT4CLicenseServer,
):
    users_crud.create_user(
        db, executor_name, executor_name, None, users_models.Role.ADMIN
    )

    response = client.get(
        f"/api/v1/settings/modelsources/t4c/license-servers/{t4c_license_server.id}",
    )

    assert response.json()["name"] == "test license server"


def test_patch_t4c_license_server(
    client: testclient.TestClient,
    db: orm.Session,
    executor_name: str,
    t4c_license_server: license_server_models.DatabaseT4CLicenseServer,
):
    users_crud.create_user(
        db, executor_name, executor_name, None, users_models.Role.ADMIN
    )

    response = client.patch(
        f"/api/v1/settings/modelsources/t4c/license-servers/{t4c_license_server.id}",
        json={
            "name": "Patched test license server",
        },
    )

    updated_license_server = license_server_crud.get_t4c_license_server_by_id(
        db, response.json()["id"]
    )
    assert updated_license_server

    assert response.status_code == 200

    assert response.json()["name"] == "Patched test license server"
    assert updated_license_server.name == "Patched test license server"

    assert response.json()["usage_api"] == "http://localhost:8086"
    assert updated_license_server.usage_api == "http://localhost:8086"


@pytest.mark.usefixtures("admin")
def test_patch_t4c_license_server_already_existing_name(
    client: testclient.TestClient,
    t4c_license_server: license_server_models.DatabaseT4CLicenseServer,
):
    license_server_name_1 = t4c_license_server.name
    license_server_name_2 = license_server_name_1 + "-2"

    client.post(
        "/api/v1/settings/modelsources/t4c/license-servers",
        json={
            "name": license_server_name_2,
            "usage_api": "http://localhost:8086",
            "license_key": "test_license_key",
        },
    )

    response = client.patch(
        f"/api/v1/settings/modelsources/t4c/license-servers/{t4c_license_server.id}",
        json={
            "name": license_server_name_2,
        },
    )

    assert response.status_code == 409

    assert (
        response.json()["detail"]["err_code"] == "RESOURCE_NAME_ALREADY_IN_USE"
    )


@pytest.mark.usefixtures("admin")
def test_delete_t4c_license_server(
    client: testclient.TestClient,
    db: orm.Session,
    t4c_license_server: license_server_models.DatabaseT4CLicenseServer,
):
    response = client.delete(
        f"/api/v1/settings/modelsources/t4c/license-servers/{t4c_license_server.id}",
    )

    assert response.status_code == 204
    assert (
        license_server_crud.get_t4c_license_server_by_id(
            db, t4c_license_server.id
        )
        is None
    )


@pytest.mark.usefixtures("mock_license_server")
def test_get_t4c_license_server_usage(
    client: testclient.TestClient,
    db: orm.Session,
    executor_name: str,
    t4c_license_server: license_server_models.DatabaseT4CLicenseServer,
):
    users_crud.create_user(
        db, executor_name, executor_name, None, users_models.Role.ADMIN
    )
    response = client.get(
        f"/api/v1/settings/modelsources/t4c/license-servers/{t4c_license_server.id}/usage",
    )

    assert response.status_code == 200
    assert response.json()["free"] == 19
    assert response.json()["total"] == 20


@responses.activate
def test_get_t4c_license_usage_no_status(
    client: testclient.TestClient,
    db: orm.Session,
    executor_name: str,
    t4c_license_server: license_server_models.DatabaseT4CLicenseServer,
):
    users_crud.create_user(
        db, executor_name, executor_name, None, users_models.Role.ADMIN
    )
    responses.get(
        "http://localhost:8086/status/json",
        status=status.HTTP_200_OK,
        json={
            "version": "1.0.0",
            "status": {"message": "No last status available."},
        },
    )

    response = client.get(
        f"/api/v1/settings/modelsources/t4c/license-servers/{t4c_license_server.id}/usage",
    )

    assert response.status_code == 422
    assert (
        response.json()["detail"]["err_code"] == "T4C_LICENSE_SERVER_NO_STATUS"
    )
