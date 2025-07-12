# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from fastapi import testclient

import capellacollab.projects.toolmodels.backups.models as pipelines_models


@pytest.mark.usefixtures("admin")
def test_get_all_pipelines(
    client: testclient.TestClient,
    pipeline: pipelines_models.DatabasePipeline,
):
    response = client.get("/api/v1/pipelines")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == pipeline.id
