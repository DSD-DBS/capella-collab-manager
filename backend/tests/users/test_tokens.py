# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import base64
import datetime
import json

import fastapi
import pytest
import responses
from fastapi import testclient

from capellacollab.__main__ import app
from capellacollab.core.authentication.basic_auth import HTTPBasicAuth
from capellacollab.users import models as users_models

POST_TOKEN = {
    "expiration_date": str(datetime.date.today()),
    "description": "test_token",
    "source": "test source",
}


@responses.activate
@pytest.mark.usefixtures("user")
def test_create_user_token(client: testclient.TestClient):
    response = client.post("/api/v1/users/current/tokens", json=POST_TOKEN)
    assert response.status_code == 200


@responses.activate
@pytest.mark.usefixtures("user")
def test_get_user_tokens(client: testclient.TestClient):
    response = client.get("/api/v1/users/current/tokens")
    assert response.status_code == 200


@responses.activate
def test_use_basic_token(
    client: testclient.TestClient,
    unauthenticated_user: users_models.User,
    monkeypatch: pytest.MonkeyPatch,
):
    async def basic_passthrough(self, request: fastapi.Request):
        return unauthenticated_user.name

    monkeypatch.setattr(HTTPBasicAuth, "__call__", basic_passthrough)
    token_string = f"{unauthenticated_user.name}:myTestPassword"
    token = base64.b64encode(token_string.encode("ascii"))
    basic_response = client.post(
        "/api/v1/users/current/tokens",
        headers={"Authorization": f"basic {token.decode('ascii')}"},
        json=POST_TOKEN,
    )

    assert basic_response.status_code == 200


@responses.activate
def test_use_wrong_basic_token(unauthenticated_user: users_models.User):
    token_string = f"{unauthenticated_user.name}:myTestPassword"
    token = base64.b64encode(token_string.encode("ascii"))
    basic_client = testclient.TestClient(app)
    basic_response = basic_client.post(
        "/api/v1/users/current/tokens",
        headers={"Authorization": f"basic {token.decode('ascii')}"},
        json=POST_TOKEN,
    )
    assert basic_response.status_code == 401


@responses.activate
def test_create_and_delete_token(
    client: testclient.TestClient, user: users_models.User
):
    response = client.post("/api/v1/users/current/tokens", json=POST_TOKEN)
    assert response.status_code == 200

    token_id = response.json()["id"]

    response = client.delete(f"/api/v1/users/current/tokens/{token_id}")
    assert response.status_code == 204


@responses.activate
def test_token_lifecycle(
    client: testclient.TestClient, user: users_models.User
):
    response = client.post("/api/v1/users/current/tokens", json=POST_TOKEN)
    assert response.status_code == 200

    response = client.get("/api/v1/users/current/tokens")
    response_string = response.content.decode("utf-8")
    assert len(json.loads(response_string)) == 1

    token_id = response.json()[0]["id"]

    response = client.delete(f"/api/v1/users/current/tokens/{token_id}")
    assert response.status_code == 204

    response = client.get("/api/v1/users/current/tokens")
    response_string = response.content.decode("utf-8")
    assert len(json.loads(response_string)) == 0
