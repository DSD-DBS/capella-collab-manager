# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime

from fastapi import testclient

from capellacollab.users.tokens import models as tokens_models


def test_invalid_basic_auth_unknown_user(
    client_unauthenticated: testclient.TestClient,
) -> None:
    response = client_unauthenticated.get(
        "/api/v1/projects", auth=("unknown_user", "test")
    )

    assert response.status_code == 401
    assert response.json()["detail"]["err_code"] == "BASIC_TOKEN_INVALID"


def test_invalid_basic_auth_expired_token(
    client_pat: testclient.TestClient,
    pat: tuple[tokens_models.DatabaseUserToken, str],
) -> None:
    pat[0].expiration_date = datetime.datetime.now(
        tz=datetime.UTC
    ).date() - datetime.timedelta(days=1)
    response = client_pat.get("/api/v1/projects")

    assert response.status_code == 401
    assert response.json()["detail"]["err_code"] == "PAT_EXPIRED"
