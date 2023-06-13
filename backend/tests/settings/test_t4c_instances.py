# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import testclient
from sqlalchemy import orm

from capellacollab.tools import crud as tools_crud
from capellacollab.users import crud as users_crud
from capellacollab.users import models as users_models


def test_create_t4c_instance(
    client: testclient.TestClient, db: orm.Session, executor_name: str
):
    users_crud.create_user(db, executor_name, users_models.Role.ADMIN)
    tool = tools_crud.create_tool_with_name(db, "Test")
    version = tools_crud.create_version(db, tool.id, "test")

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
            "version_id": version.id,
            "password": "secret-password",
        },
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Test integration"
