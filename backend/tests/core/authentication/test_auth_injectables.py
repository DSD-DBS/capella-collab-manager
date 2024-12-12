# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import testclient


def test_authentication_unknown_scheme(
    client_unauthenticated: testclient.TestClient,
):
    response = client_unauthenticated.get(
        "/api/v1/projects", headers={"Authorization": "bearer XXX"}
    )
    assert response.status_code == 401
    assert response.json()["detail"]["err_code"] == "UNKNOWN_SCHEME"
