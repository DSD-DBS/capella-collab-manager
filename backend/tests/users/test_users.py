# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import kubernetes
import prometheus_client.samples
import pytest
from fastapi import testclient
from sqlalchemy import orm

import capellacollab.projects.users.models as projects_users_models
from capellacollab.events import crud as events_crud
from capellacollab.events import models as events_models
from capellacollab.projects import models as projects_models
from capellacollab.projects.users import crud as projects_users_crud
from capellacollab.users import crud as users_crud
from capellacollab.users import metrics as users_metrics
from capellacollab.users import models as users_models
from capellacollab.users.workspaces import crud as user_workspace_crud
from capellacollab.users.workspaces import models as user_workspace_models


@pytest.mark.usefixtures("admin")
def test_get_user_by_id_admin(
    client: testclient.TestClient,
    db: orm.Session,
):
    user = users_crud.create_user(db, "test_user", "test_user")
    response = client.get(f"/api/v1/users/{user.id}")

    assert response.status_code == 200
    assert response.json()["name"] == "test_user"


@pytest.mark.usefixtures("user")
def test_get_user_by_id_non_admin(
    client: testclient.TestClient, db: orm.Session
):
    user = users_crud.create_user(db, "test_user", "test_user")
    response = client.get(f"/api/v1/users/{user.id}")

    assert response.status_code == 403


@pytest.mark.usefixtures("project_user")
def test_get_user_by_id_common_project(
    client: testclient.TestClient,
    db: orm.Session,
    project: projects_models.DatabaseProject,
):
    user2 = users_crud.create_user(db, "user2", "user2")
    projects_users_crud.add_user_to_project(
        db,
        project,
        user2,
        role=projects_users_models.ProjectUserRole.USER,
        permission=projects_users_models.ProjectUserPermission.WRITE,
    )

    response = client.get(f"/api/v1/users/{user2.id}")
    assert response.status_code == 200
    assert response.json()["name"] == "user2"


@pytest.mark.usefixtures("user")
def test_get_no_common_projects(
    client: testclient.TestClient, db: orm.Session
):
    user2 = users_crud.create_user(db, "user2", "user2")
    response = client.get(f"/api/v1/users/{user2.id}/common-projects")
    assert response.status_code == 200
    assert len(response.json()) == 0


@pytest.mark.usefixtures("project_user")
def test_get_common_projects(
    client: testclient.TestClient,
    db: orm.Session,
    project: projects_models.DatabaseProject,
):
    user2 = users_crud.create_user(db, "user2", "user2")
    projects_users_crud.add_user_to_project(
        db,
        project,
        user2,
        role=projects_users_models.ProjectUserRole.USER,
        permission=projects_users_models.ProjectUserPermission.WRITE,
    )

    response = client.get(f"/api/v1/users/{user2.id}/common-projects")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["slug"] == project.slug


@pytest.mark.usefixtures("admin")
def test_delete_user(
    client: testclient.TestClient,
    db: orm.Session,
    admin: users_models.DatabaseUser,
    test_user: users_models.DatabaseUser,
    monkeypatch: pytest.MonkeyPatch,
):
    event = events_crud.create_event(
        db,
        test_user,
        events_models.EventType.CREATED_USER,
        executor=admin,
    )
    workspace = user_workspace_crud.create_workspace(
        db, user_workspace_models.DatabaseWorkspace("test", "1Gi", test_user)
    )

    monkeypatch.setattr(
        kubernetes.client.CoreV1Api,
        "delete_namespaced_persistent_volume_claim",
        lambda self, name, namespace: kubernetes.client.V1Status(),
    )

    response = client.delete(f"/api/v1/users/{test_user.id}")

    assert response.status_code == 204
    assert users_crud.get_user_by_id(db, test_user.id) is None
    with pytest.raises(orm.exc.ObjectDeletedError):
        events_crud.get_event_by_id(db, event.id)
    assert (
        user_workspace_crud.get_workspace_by_id_and_user(
            db, test_user, workspace.id
        )
        is None
    )


def test_fail_update_own_user(
    client: testclient.TestClient, user: users_models.DatabaseUser
):
    response = client.patch(
        f"/api/v1/users/{user.id}", json={"name": "new_name"}
    )

    assert response.status_code == 403
    assert (
        response.json()["detail"]["err_code"] == "CHANGES_NOT_ALLOWED_FOR_ROLE"
    )


def test_user_metrics(db: orm.Session):
    """Test that user metrics correctly count beta and non-beta users."""

    def get_metric() -> tuple[
        prometheus_client.samples.Sample, prometheus_client.samples.Sample
    ]:
        collector = users_metrics.UserCountCollector()
        data = list(collector.collect())
        metric = data[0]

        beta_sample = next(
            s for s in metric.samples if s.labels["beta"] == "true"
        )
        non_beta_sample = next(
            s for s in metric.samples if s.labels["beta"] == "false"
        )

        return beta_sample, non_beta_sample

    base_beta, base_non_beta = get_metric()

    user1 = users_crud.create_user(db, "regular_user1", "regular_user1")

    new_beta, new_non_beta = get_metric()
    assert new_beta.value == base_beta.value
    assert new_non_beta.value == base_non_beta.value + 1

    users_crud.update_user(db, user1, users_models.PatchUser(beta_tester=True))

    new_beta, new_non_beta = get_metric()
    assert new_beta.value == base_beta.value + 1
    assert new_non_beta.value == base_non_beta.value


@pytest.mark.usefixtures("admin")
def test_get_users(
    client: testclient.TestClient,
    executor_name: str,
):
    response = client.get("/api/v1/users")

    assert response.status_code == 200
    assert len(response.json()) >= 2
    assert any(user["name"] == "admin" for user in response.json())
    assert any(user["name"] == executor_name for user in response.json())


@pytest.mark.usefixtures("admin")
def test_fail_update_user_no_reason(
    client: testclient.TestClient,
    test_user: users_models.DatabaseUser,
):
    response = client.patch(
        f"/api/v1/users/{test_user.id}", json={"role": users_models.Role.ADMIN}
    )

    assert response.status_code == 403
    assert (
        response.json()["detail"]["err_code"] == "ROLE_UPDATE_REQUIRES_REASON"
    )
