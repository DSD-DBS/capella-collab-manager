# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import json
import pathlib
import tarfile

import kubernetes.client
import kubernetes.config
import pytest
from websocket import ABNF

from capellacollab.cli.ws import backup, ls, restore, volumes


@pytest.fixture(autouse=True)
def mock_kube_config(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("kubernetes.config.load_kube_config", lambda: None)


@pytest.fixture(autouse=True)
def mock_core_v1_api(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        "kubernetes.client.CoreV1Api.create_namespaced_pod",
        lambda self, ns, pod: pod,
    )
    monkeypatch.setattr(
        "kubernetes.client.CoreV1Api.delete_namespaced_pod",
        lambda self, name, ns: None,
    )
    monkeypatch.setattr(
        "kubernetes.client.CoreV1Api.read_namespaced_pod_status",
        lambda self, name, namespace: kubernetes.client.V1Pod(
            status=kubernetes.client.V1PodStatus(phase="Running")
        ),
    )
    monkeypatch.setattr(
        "kubernetes.client.CoreV1Api.create_namespaced_persistent_volume_claim",
        lambda self, ns, pvc: None,
    )


def test_workspace_volumes(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
):
    def pvc_factory(
        name: str, labels: dict[str, str] | None = None
    ) -> kubernetes.client.V1PersistentVolumeClaim:
        return kubernetes.client.V1PersistentVolumeClaim(
            metadata=kubernetes.client.V1ObjectMeta(
                name=name,
                labels=labels,
                creation_timestamp=datetime.datetime.now(datetime.UTC),
            ),
            spec=kubernetes.client.V1PersistentVolumeClaimSpec(
                access_modes=["ReadWriteOnce"],
                resources=kubernetes.client.V1ResourceRequirements(
                    requests={"storage": "1Gi"}
                ),
            ),
        )

    pvcs = [
        pvc_factory("workspace-test2"),
        pvc_factory("persistent-session-test"),  # Legacy PVC names
        pvc_factory("shared-workspace-project-test"),
        pvc_factory(
            "shared-workspace-2342352342",
            labels={"capellacollab/project_slug": "project-test"},
        ),
        pvc_factory("my-volume"),
    ]

    monkeypatch.setattr(
        "kubernetes.client.CoreV1Api.list_namespaced_persistent_volume_claim",
        lambda self,
        namespace,
        watch: kubernetes.client.V1PersistentVolumeClaimList(items=pvcs),
    )

    volumes(namespace="default")

    stdout = capsys.readouterr().out
    for pvc in pvcs:
        assert pvc.metadata.name in stdout


def test_ls_workspace(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
):
    mock_stream = MockWSClient([b"\01hello"])
    monkeypatch.setattr(
        "kubernetes.stream.stream", lambda *a, **ka: mock_stream
    )
    monkeypatch.setattr("select.select", lambda *a: (1, None, None))

    ls("my-volume-name", namespace="my-namespace")

    assert "hello" in capsys.readouterr().out


def test_backup_workspace(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path
):
    mock_stream = MockWSClient([b"\01hello"])
    monkeypatch.setattr(
        "kubernetes.stream.stream", lambda *a, **ka: mock_stream
    )
    monkeypatch.setattr("select.select", lambda *a: (1, None, None))

    monkeypatch.setattr(
        kubernetes.client.CoreV1Api,
        "read_namespaced_persistent_volume_claim",
        lambda self,
        name,
        namespace: kubernetes.client.V1PersistentVolumeClaim(
            spec=kubernetes.client.V1PersistentVolumeClaimSpec(
                resources=kubernetes.client.V1ResourceRequirements(
                    requests={"storage": "1Gi"},
                ),
            ),
            metadata=kubernetes.client.V1ObjectMeta(
                annotations={
                    "capellacollab/username": "test",
                    "capellacollab/user-id": str(10),
                    "capellacollab/volume": "personal-workspace",
                },
            ),
        ),
    )

    backup("my-volume-name", "my-namespace", tmp_path)
    assert (tmp_path / "my-volume-name.tar.gz").exists()

    sidecar_path = tmp_path / "my-volume-name.json"
    assert sidecar_path.exists()

    sidecar = json.loads(sidecar_path.read_text())

    assert sidecar.get("size") == "1Gi"
    assert sidecar.get("annotations").get("capellacollab/username") == "test"


def test_restore_workspace_without_sidecar(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path
):
    pvc_created = False

    def mock_create_namespaced_persistent_volume_claim(
        self,
        namespace: str,
        pvc: kubernetes.client.V1PersistentVolumeClaim,
    ):
        assert namespace == "default"
        assert pvc.metadata.name == "my-volume-name"
        assert pvc.spec.resources.requests["storage"] == "20Gi"
        assert not pvc.metadata.annotations

        nonlocal pvc_created
        pvc_created = True

    monkeypatch.setattr(
        kubernetes.client.CoreV1Api,
        "create_namespaced_persistent_volume_claim",
        mock_create_namespaced_persistent_volume_claim,
    )

    mock_stream = MockWSClient([])
    monkeypatch.setattr(
        "kubernetes.stream.stream", lambda *a, **ka: mock_stream
    )

    tar_path = tmp_path / "backup.tar.gz"
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add("tests")

    restore("my-volume-name", tar_path, "default")

    assert mock_stream.written_data
    assert pvc_created


def test_restore_workspace_with_sidecar(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path
):
    pvc_created = False

    sidecar_path = tmp_path / "backup.json"
    sidecar_path.write_text(
        json.dumps({"size": "1Gi", "annotations": {"foo": "bar"}})
    )

    def mock_create_namespaced_persistent_volume_claim(
        self,
        namespace: str,
        pvc: kubernetes.client.V1PersistentVolumeClaim,
    ):
        assert namespace == "default"
        assert pvc.metadata.name == "my-volume-name"
        assert pvc.spec.resources.requests["storage"] == "1Gi"
        assert pvc.metadata.annotations["foo"] == "bar"

        nonlocal pvc_created
        pvc_created = True

    monkeypatch.setattr(
        kubernetes.client.CoreV1Api,
        "create_namespaced_persistent_volume_claim",
        mock_create_namespaced_persistent_volume_claim,
    )

    mock_stream = MockWSClient([])
    monkeypatch.setattr(
        "kubernetes.stream.stream", lambda *a, **ka: mock_stream
    )

    tar_path = tmp_path / "backup.tar.gz"
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add("tests")

    restore("my-volume-name", tar_path, "default", sidecar_path)

    assert mock_stream.written_data
    assert pvc_created


class MockWSClient:
    def __init__(self, blocks):
        self._blocks = blocks
        self._connected = True
        self.sock = self
        self.written_data = []

    @property
    def connected(self):
        return self._connected

    def is_open(self):
        return self._connected

    def close(self):
        self._connected = False

    def recv_data_frame(self, wait):
        if self._blocks:
            return ABNF.OPCODE_BINARY, Frame(self._blocks.pop(0))
        self._connected = False
        return ABNF.OPCODE_CLOSE, None

    def update(self, timeout=0):
        pass

    def peek_stdout(self):
        return None

    def peek_stderr(self):
        return None

    def write_stdin(self, data):
        self.written_data.append(data)


class Frame:
    def __init__(self, data):
        self.data = data
