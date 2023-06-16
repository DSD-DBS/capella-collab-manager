# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
import responses
from fastapi import status, testclient
from sqlalchemy import orm

from capellacollab.settings.modelsources.t4c import crud as t4c_crud
from capellacollab.settings.modelsources.t4c import models as t4c_models
from capellacollab.tools import crud as tools_crud
from capellacollab.tools import models as tools_models
from capellacollab.users import crud as users_crud
from capellacollab.users import models as users_models


@pytest.fixture(name="test_tool_version")
def fixture_test_tool_version(db: orm.Session) -> tools_models.Version:
    tool = tools_crud.create_tool_with_name(db, "Test")
    return tools_crud.create_version(db, tool.id, "test")


@pytest.fixture(name="admin_user")
def fixture_admin_user(
    db: orm.Session, executor_name: str
) -> users_models.DatabaseUser:
    return users_crud.create_user(db, executor_name, users_models.Role.ADMIN)


@pytest.fixture(name="t4c_server")
def fixture_t4c_server(
    db: orm.Session,
    test_tool_version: tools_models.Version,
) -> t4c_models.DatabaseT4CInstance:
    server = t4c_models.DatabaseT4CInstance(
        name="test server",
        license="lic",
        host="localhost",
        usage_api="http://localhost:8086",
        rest_api="http://localhost:8080/api/v1.0",
        username="user",
        password="pass",
        protocol=t4c_models.Protocol.tcp,
        version=test_tool_version,
    )

    return t4c_crud.create_t4c_instance(db, server)


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

    assert (
        t4c_crud.get_t4c_instance_by_id(db, response.json()["id"]).name
        == "Test integration"
    )


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

    assert response.json()["name"] == "Patched test integration"
    assert (
        t4c_crud.get_t4c_instance_by_id(db, response.json()["id"]).name
        == "Patched test integration"
    )

    assert response.json()["host"] == "localhost"
    assert (
        t4c_crud.get_t4c_instance_by_id(db, response.json()["id"]).host
        == "localhost"
    )


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
