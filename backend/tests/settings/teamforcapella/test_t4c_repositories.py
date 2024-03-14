# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
import responses
from fastapi import testclient
from sqlalchemy import orm

from capellacollab.settings.modelsources.t4c import models as t4c_models
from capellacollab.settings.modelsources.t4c.repositories import (
    crud as t4c_repositories_crud,
)


@responses.activate
@pytest.mark.usefixtures("admin_user")
def test_list_t4c_repositories(
    client: testclient.TestClient,
    db: orm.Session,
    t4c_instance: t4c_models.DatabaseT4CInstance,
):
    responses.get(
        "http://localhost:8080/api/v1.0/repositories",
        status=200,
        json={
            "repositories": [
                {
                    "name": "test1",
                    "status": "ONLINE",
                },
                {"name": "test2", "status": "OFFLINE"},
                {"name": "test3", "status": "INITIAL"},
                {"name": "test4", "status": "ONLINE"},
            ]
        },
    )

    t4c_repositories_crud.create_t4c_repository(db, "test4", t4c_instance)
    t4c_repositories_crud.create_t4c_repository(db, "test5", t4c_instance)
    response = client.get(
        f"/api/v1/settings/modelsources/t4c/{t4c_instance.id}/repositories",
    )

    assert response.status_code == 200
    assert len(response.json()["payload"]) == 5

    transformed_response = {
        repo["name"]: repo["status"] for repo in response.json()["payload"]
    }
    assert transformed_response["test1"] == "ONLINE"
    assert transformed_response["test2"] == "OFFLINE"
    assert transformed_response["test3"] == "INITIAL"
    assert transformed_response["test4"] == "ONLINE"
    assert transformed_response["test5"] == "NOT_FOUND"
