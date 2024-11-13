# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import kubernetes
import pytest
from kubernetes.client import exceptions
from sqlalchemy import orm

from capellacollab.sessions import exceptions as sessions_exceptions
from capellacollab.sessions import models as sessions_models
from capellacollab.sessions import operators
from capellacollab.sessions.hooks import interface as hooks_interface
from capellacollab.sessions.hooks import persistent_workspace
from capellacollab.users import models as users_models
from capellacollab.users.workspaces import crud as users_workspaces_crud
from capellacollab.users.workspaces import models as users_workspaces_models


def test_persistent_workspace_mounting_not_allowed(
    configuration_hook_request: hooks_interface.ConfigurationHookRequest,
):
    configuration_hook_request.tool.config.persistent_workspaces.mounting_enabled = (
        False
    )

    with pytest.raises(sessions_exceptions.WorkspaceMountingNotAllowedError):
        persistent_workspace.PersistentWorkspaceHook().configuration_hook(
            configuration_hook_request
        )


def persistent_workspace_mounting_readonly_session(
    configuration_hook_request: hooks_interface.ConfigurationHookRequest,
):
    configuration_hook_request.session_type = (
        sessions_models.SessionType.READONLY
    )

    response = (
        persistent_workspace.PersistentWorkspaceHook().configuration_hook(
            configuration_hook_request
        )
    )

    assert response == hooks_interface.ConfigurationHookResult()


def test_workspace_is_created(
    db: orm.Session,
    test_user: users_models.DatabaseUser,
    monkeypatch: pytest.MonkeyPatch,
    configuration_hook_request: hooks_interface.ConfigurationHookRequest,
):
    created_volumes = 0
    volume_name = None

    def mock_create_namespaced_persistent_volume_claim(
        # pylint: disable=unused-argument
        self,
        ns: str,
        pvc: kubernetes.client.V1PersistentVolumeClaim,
    ):
        nonlocal created_volumes, volume_name
        created_volumes += 1
        volume_name = pvc.metadata.name

    monkeypatch.setattr(
        kubernetes.client.CoreV1Api,
        "create_namespaced_persistent_volume_claim",
        mock_create_namespaced_persistent_volume_claim,
    )

    assert (
        len(users_workspaces_crud.get_workspaces_for_user(db, test_user)) == 0
    )

    configuration_hook_request.operator = operators.KubernetesOperator()
    configuration_hook_request.user = test_user
    persistent_workspace.PersistentWorkspaceHook().configuration_hook(
        configuration_hook_request
    )
    assert created_volumes == 1
    assert isinstance(volume_name, str)
    assert volume_name.startswith("workspace-")
    assert (
        len(users_workspaces_crud.get_workspaces_for_user(db, test_user)) == 1
    )


def test_existing_workspace_is_mounted(
    db: orm.Session,
    test_user: users_models.DatabaseUser,
    user_workspace: users_workspaces_models.DatabaseWorkspace,
    monkeypatch: pytest.MonkeyPatch,
    configuration_hook_request: hooks_interface.ConfigurationHookRequest,
):
    created_volumes = 0
    volume_name = None

    # pylint: disable=unused-argument
    def mock_create_namespaced_persistent_volume_claim(self, ns, pvc):
        nonlocal created_volumes, volume_name
        created_volumes += 1
        volume_name = pvc.metadata.name
        raise exceptions.ApiException(status=409)

    monkeypatch.setattr(
        "kubernetes.client.CoreV1Api.create_namespaced_persistent_volume_claim",
        mock_create_namespaced_persistent_volume_claim,
    )

    assert (
        len(users_workspaces_crud.get_workspaces_for_user(db, test_user)) == 1
    )

    configuration_hook_request.user = test_user
    configuration_hook_request.operator = operators.KubernetesOperator()
    persistent_workspace.PersistentWorkspaceHook().configuration_hook(
        configuration_hook_request
    )
    assert created_volumes == 1
    assert isinstance(volume_name, str)
    assert volume_name == user_workspace.pvc_name
    assert (
        len(users_workspaces_crud.get_workspaces_for_user(db, test_user)) == 1
    )
