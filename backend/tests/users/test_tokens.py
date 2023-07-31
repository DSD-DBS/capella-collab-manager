# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import base64

import pytest
import responses
from fastapi import testclient

from capellacollab.users import models as user_models


@responses.activate
@pytest.mark.usefixtures("user")
def test_get_user_token(client: testclient.TestClient):
    response = client.post(f"/api/v1/users/current/token")
    assert response.status_code == 200


@responses.activate
def test_get_and_use_basic_token(
    client: testclient.TestClient, user: user_models.User
):
    response = client.post(f"/api/v1/users/current/token")
    assert response.status_code == 200

    password = response.content.decode("ascii").replace('"', "")
    token_string = user.name + ":" + password
    token = base64.b64encode(token_string.encode("ascii"))
    basic_response = client.post(
        f"/api/v1/users/current/token",
        headers={"Authorization": f"basic {token.decode('ascii')}"},
    )
    assert basic_response.status_code == 200
