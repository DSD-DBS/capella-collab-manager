# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from fastapi import testclient
from sqlalchemy import orm

from capellacollab.tags import crud as tags_crud
from capellacollab.tags import models as tags_models


@pytest.mark.usefixtures("user")
def test_get_tags(
    client: testclient.TestClient,
    tag: tags_models.DatabaseTag,
):
    response = client.get("/api/v1/tags")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == tag.name


@pytest.mark.usefixtures("admin")
def test_create_tag(
    client: testclient.TestClient,
):
    response = client.post(
        "/api/v1/tags",
        json={
            "name": "Example tag",
            "description": "This is an example tag",
            "hex_color": "#FF5733",
            "icon": "check",
        },
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Example tag"


@pytest.mark.usefixtures("admin")
def test_update_tag(
    client: testclient.TestClient,
    tag: tags_models.DatabaseTag,
):
    response = client.put(
        f"/api/v1/tags/{tag.id}",
        json={
            "name": "Example tag 2",
            "description": "This is an example tag",
            "hex_color": "#FF5733",
            "icon": "check",
        },
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Example tag 2"


@pytest.mark.usefixtures("admin")
def test_delete_tag(
    client: testclient.TestClient,
    db: orm.Session,
    tag: tags_models.DatabaseTag,
):
    response = client.delete(f"/api/v1/tags/{tag.id}")
    assert response.status_code == 204
    assert tags_crud.get_tag_by_id(db, tag.id) is None
