# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import kubernetes
import pytest
from fastapi import testclient
from sqlalchemy import orm

from capellacollab.users import models as users_models
from capellacollab.users.workspaces import crud as user_workspace_crud
from capellacollab.users.workspaces import models as user_workspace_models


@pytest.mark.usefixtures("admin")
def test_get_workspaces(
    client: testclient.TestClient,
    test_user: users_models.DatabaseUser,
    user_workspace: user_workspace_models.DatabaseWorkspace,
):
    response = client.get(f"/api/v1/users/{test_user.id}/workspaces")
    assert len(response.json()) == 1
    assert response.json()[0]["pvc_name"] == user_workspace.pvc_name


@pytest.mark.usefixtures("admin")
def test_delete_workspaces_404(
    client: testclient.TestClient,
    test_user: users_models.DatabaseUser,
):
    response = client.delete(f"/api/v1/users/{test_user.id}/workspaces/0")
    assert response.status_code == 404
    assert response.json()["detail"]["err_code"] == "USER_WORKSPACE_NOT_FOUND"


@pytest.mark.usefixtures("admin")
def test_delete_workspace(
    client: testclient.TestClient,
    db: orm.Session,
    test_user: users_models.DatabaseUser,
    user_workspace: user_workspace_models.DatabaseWorkspace,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(
        kubernetes.client.CoreV1Api,
        "delete_namespaced_persistent_volume_claim",
        lambda self, name, namespace: kubernetes.client.V1Status(),
    )

    response = client.delete(
        f"/api/v1/users/{test_user.id}/workspaces/{user_workspace.id}"
    )

    assert response.status_code == 204
    assert (
        user_workspace_crud.get_workspace_by_id_and_user(
            db, test_user, user_workspace.id
        )
        is None
    )


@pytest.mark.usefixtures("admin", "test_session")
def test_delete_workspace_with_open_sessions(
    client: testclient.TestClient,
    test_user: users_models.DatabaseUser,
    user_workspace: user_workspace_models.DatabaseWorkspace,
):
    response = client.delete(
        f"/api/v1/users/{test_user.id}/workspaces/{user_workspace.id}"
    )

    assert response.status_code == 409
    assert (
        response.json()["detail"]["err_code"]
        == "EXISTING_DEPENDENCIES_PREVENT_DELETE"
    )
