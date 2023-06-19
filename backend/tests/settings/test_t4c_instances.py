# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
import responses
from fastapi import status, testclient
from sqlalchemy import orm

from capellacollab.settings.modelsources.t4c import crud as t4c_crud
from capellacollab.settings.modelsources.t4c import models as t4c_models
from capellacollab.tools import models as tools_models
from capellacollab.users import crud as users_crud
from capellacollab.users import models as users_models


@pytest.mark.usefixtures("admin_user")
def test_create_t4c_instance(
    client: testclient.TestClient,
    db: orm.Session,
    test_tool_version: tools_models.Version,
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
            "version_id": test_tool_version.id,
            "password": "secret-password",
        },
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Test integration"

    t4c_instance = t4c_crud.get_t4c_instance_by_id(db, response.json()["id"])

    assert t4c_instance
    assert t4c_instance.name == "Test integration"


@pytest.mark.usefixtures("t4c_server")
def test_get_t4c_instances(
    client: testclient.TestClient, db: orm.Session, executor_name: str
):
    users_crud.create_user(db, executor_name, users_models.Role.ADMIN)

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
    t4c_server: t4c_models.DatabaseT4CInstance,
):
    users_crud.create_user(db, executor_name, users_models.Role.ADMIN)

    response = client.get(
        f"/api/v1/settings/modelsources/t4c/{t4c_server.id}",
    )

    assert response.json()["name"] == "test server"

    # Password should not be exposed via API
    assert "password" not in response.json()


def test_patch_t4c_instance(
    client: testclient.TestClient,
    db: orm.Session,
    executor_name: str,
    t4c_server: t4c_models.DatabaseT4CInstance,
):
    users_crud.create_user(db, executor_name, users_models.Role.ADMIN)

    response = client.patch(
        f"/api/v1/settings/modelsources/t4c/{t4c_server.id}",
        json={
            "name": "Patched test integration",
        },
    )

    t4c_instance = t4c_crud.get_t4c_instance_by_id(db, response.json()["id"])
    assert t4c_instance

    assert response.json()["name"] == "Patched test integration"
    assert t4c_instance.name == "Patched test integration"

    assert response.json()["host"] == "localhost"
    assert t4c_instance.host == "localhost"


@responses.activate
def test_get_t4c_license_usage(
    client: testclient.TestClient,
    db: orm.Session,
    executor_name: str,
    t4c_server: t4c_models.DatabaseT4CInstance,
):
    users_crud.create_user(db, executor_name, users_models.Role.ADMIN)
    responses.get(
        "http://localhost:8086/status/json",
        status=status.HTTP_200_OK,
        json={"status": {"used": 1, "free": 19, "total": 20}},
    )

    response = client.get(
        f"/api/v1/settings/modelsources/t4c/{t4c_server.id}/licenses",
    )

    assert response.status_code == 200
    assert response.json()["free"] == 19
    assert response.json()["total"] == 20


@responses.activate
def test_get_t4c_license_usage_no_status(
    client: testclient.TestClient,
    db: orm.Session,
    executor_name: str,
    t4c_server: t4c_models.DatabaseT4CInstance,
):
    users_crud.create_user(db, executor_name, users_models.Role.ADMIN)
    responses.get(
        "http://localhost:8086/status/json",
        status=status.HTTP_200_OK,
        json={"status": {"message": "No last status available."}},
    )

    response = client.get(
        f"/api/v1/settings/modelsources/t4c/{t4c_server.id}/licenses",
    )

    assert response.status_code == 502
    assert response.json()["detail"]["err_code"] == "NO_STATUS"
