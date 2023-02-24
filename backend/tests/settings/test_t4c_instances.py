# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from capellacollab.tools import crud as tools_crud
from capellacollab.tools import models as tools_models
from capellacollab.users.crud import create_user
from capellacollab.users.models import Role


def test_create_t4c_instance(
    client: TestClient, db: Session, executor_name: str
):
    create_user(db, executor_name, Role.ADMIN)
    tool = tools_crud.create_tool(db, tools_models.Tool(name="Test"))
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
