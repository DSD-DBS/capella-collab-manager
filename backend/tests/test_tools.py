# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from fastapi import testclient


@pytest.mark.usefixtures("project_manager")
def test_get_tools(client: testclient.TestClient, development_mode: bool):
    response = client.get("/api/v1/tools")
    out = response.json()

    assert response.status_code == 200
    assert "Capella" in (tool["name"] for tool in out)
    if development_mode:
        assert "Papyrus" in (tool["name"] for tool in out)
