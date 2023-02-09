# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


def test_get_tools(client, project_manager):

    response = client.get("/api/v1/tools")
    out = response.json()

    assert response.status_code == 200
    assert "Capella" in (tool["name"] for tool in out)
    assert "Papyrus" in (tool["name"] for tool in out)
