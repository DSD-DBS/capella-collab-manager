# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from fastapi import testclient


@pytest.mark.usefixtures("project_manager")
def test_get_tools(client: testclient.TestClient):
    response = client.get("/api/v1/tools")
    out = response.json()

    assert response.status_code == 200
    assert "Capella" in (tool["name"] for tool in out)
