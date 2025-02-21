# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import pytest

from capellacollab.projects.users import models as projects_users_models
from capellacollab.projects.volumes import models as projects_volumes_models
from capellacollab.sessions import models as sessions_models
from capellacollab.sessions.hooks import interface as hooks_interface
from capellacollab.sessions.hooks import project_volume as project_volume_hook
from capellacollab.sessions.operators import k8s
from capellacollab.sessions.operators import models as operators_models


@pytest.fixture(name="mock_persistent_volume_exists")
def fixture_mock_persistent_volume_exists(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        k8s.KubernetesOperator,
        "persistent_volume_exists",
        lambda self, name: True,
    )


@pytest.fixture(name="mock_operator_calls", autouse=True)
def fixture_mock_operator_calls(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(
        k8s.KubernetesOperator, "delete_config_map", lambda self, name: None
    )
    monkeypatch.setattr(
        k8s.KubernetesOperator,
        "create_config_map",
        lambda self, name, data: None,
    )


@pytest.mark.usefixtures("mock_persistent_volume_exists")
def test_volume_mount_read_only_user(
    configuration_hook_request: hooks_interface.ConfigurationHookRequest,
    project_volume: projects_volumes_models.DatabaseProjectVolume,
    project_user: projects_users_models.DatabaseProjectUserAssociation,
):
    """Test that a volume is mounted as read-only if the user has only read access"""
    project_user.permission = projects_users_models.ProjectUserPermission.READ
    result = project_volume_hook.ProjectVolumeIntegration().configuration_hook(
        configuration_hook_request
    )

    assert not result["warnings"]
    assert len(result["volumes"]) == 2

    volume = result["volumes"][0]
    assert isinstance(volume, operators_models.PersistentVolume)
    assert volume.name == project_volume.pvc_name
    assert volume.read_only is True


@pytest.mark.usefixtures("project_volume", "mock_persistent_volume_exists")
def test_volume_not_mounted_without_access(
    configuration_hook_request: hooks_interface.ConfigurationHookRequest,
):
    result = project_volume_hook.ProjectVolumeIntegration().configuration_hook(
        configuration_hook_request
    )

    assert not result["warnings"]
    assert len(result["volumes"]) == 1


@pytest.mark.usefixtures("project_user", "mock_persistent_volume_exists")
def test_volume_mount_write_user(
    configuration_hook_request: hooks_interface.ConfigurationHookRequest,
    project_volume: projects_volumes_models.DatabaseProjectVolume,
):
    """Test that a volume is mounted with write access if the user has write access"""
    result = project_volume_hook.ProjectVolumeIntegration().configuration_hook(
        configuration_hook_request
    )

    assert not result["warnings"]
    assert len(result["volumes"]) == 2

    volume = result["volumes"][0]
    assert isinstance(volume, operators_models.PersistentVolume)
    assert volume.name == project_volume.pvc_name
    assert volume.read_only is False


@pytest.mark.usefixtures(
    "project_user", "project_volume", "mock_persistent_volume_exists"
)
def test_volume_mount_provisioning(
    configuration_hook_request: hooks_interface.ConfigurationHookRequest,
):
    """Test that a volume is not mounted if the project is not part of the provisioning"""

    configuration_hook_request.provisioning = [
        sessions_models.SessionProvisioningRequest(
            project_slug="test",
            model_slug="test",
            git_model_id=-1,
            deep_clone=False,
        )
    ]

    result = project_volume_hook.ProjectVolumeIntegration().configuration_hook(
        configuration_hook_request
    )

    assert not result["warnings"]
    assert len(result["volumes"]) == 1


@pytest.mark.usefixtures("project_user", "mock_persistent_volume_exists")
def test_volume_mount_read_only_provisioning(
    configuration_hook_request: hooks_interface.ConfigurationHookRequest,
    project_volume: projects_volumes_models.DatabaseProjectVolume,
):
    """Test that a volume is not mounted as read-only if the session is a read-only session"""

    configuration_hook_request.session_type = (
        sessions_models.SessionType.READONLY
    )

    result = project_volume_hook.ProjectVolumeIntegration().configuration_hook(
        configuration_hook_request
    )

    assert not result["warnings"]
    assert len(result["volumes"]) == 2

    volume = result["volumes"][0]
    assert isinstance(volume, operators_models.PersistentVolume)
    assert volume.name == project_volume.pvc_name
    assert volume.read_only is True


@pytest.mark.usefixtures("project_user", "project_volume")
def test_volume_mount_not_found_by_operator(
    configuration_hook_request: hooks_interface.ConfigurationHookRequest,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that a warning is raised if a volume is not found by the operator"""

    monkeypatch.setattr(
        k8s.KubernetesOperator,
        "persistent_volume_exists",
        lambda self, name: False,
    )

    result = project_volume_hook.ProjectVolumeIntegration().configuration_hook(
        configuration_hook_request
    )

    assert len(result["volumes"]) == 1
    assert len(result["warnings"]) == 1
    assert (
        result["warnings"][0].err_code == "PROJECT_FILE_SHARE_VOLUME_NOT_FOUND"
    )
