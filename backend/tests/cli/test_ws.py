# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import kubernetes.client
import kubernetes.config
import pytest
from websocket import ABNF

from capellacollab.cli.ws import backup, ls, volumes


@pytest.fixture(autouse=True)
def mock_kube_config(monkeypatch):
    monkeypatch.setattr("kubernetes.config.load_kube_config", lambda: None)


@pytest.fixture(autouse=True)
def mock_core_v1_api(monkeypatch):
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


def test_workspace_volumes(monkeypatch, capsys):
    monkeypatch.setattr(
        "kubernetes.client.CoreV1Api.list_namespaced_persistent_volume_claim",
        lambda self, namespace, watch: kubernetes.client.V1PersistentVolumeClaimList(
            items=[
                kubernetes.client.V1PersistentVolumeClaim(
                    metadata=kubernetes.client.V1ObjectMeta(name="my-volume")
                )
            ]
        ),
    )

    volumes(namespace="default")

    assert "my-volume" in capsys.readouterr().out


def test_ls_workspace(monkeypatch, tmp_path, capsys):
    mock_stream = MockWSClient([b"\01hello"])
    monkeypatch.setattr(
        "kubernetes.stream.stream", lambda *a, **ka: mock_stream
    )
    monkeypatch.setattr("select.select", lambda *a: (1, None, None))

    ls("my-volume-name", namespace="my-namespace")

    assert "hello" in capsys.readouterr().out


def test_backup_workspace(monkeypatch, tmp_path):
    mock_stream = MockWSClient([b"\01hello"])
    monkeypatch.setattr(
        "kubernetes.stream.stream", lambda *a, **ka: mock_stream
    )
    monkeypatch.setattr("select.select", lambda *a: (1, None, None))

    backup("my-volume-name", "my-namespace", tmp_path)

    assert (tmp_path / "my-volume-name.tar.gz").exists()


class MockWSClient:
    def __init__(self, blocks):
        self._blocks = blocks
        self._connected = True
        self.sock = self

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
        else:
            self._connected = False
            return ABNF.OPCODE_CLOSE, None


class Frame:
    def __init__(self, data):
        self.data = data
