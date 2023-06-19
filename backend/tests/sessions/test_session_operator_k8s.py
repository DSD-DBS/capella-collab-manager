# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import base64
import os

import pytest

if not os.getenv("CI"):
    from capellacollab.sessions.operators.k8s import (
        KubernetesOperator,
        lazy_b64decode,
    )

hello = base64.b64encode(b"hello")  # aGVsbG8=


@pytest.mark.skip
def test_lazy_b64_decode():
    assert as_text(lazy_b64decode([hello])) == "hello"
    assert (
        as_text(lazy_b64decode([hello[0:3], hello[3:7], hello[7:]])) == "hello"
    )
    assert (
        as_text(
            lazy_b64decode(
                [hello[0:1], hello[1:2], hello[2:3], hello[3:4], hello[4:]]
            )
        )
        == "hello"
    )


@pytest.mark.skip
def test_download_file(monkeypatch):
    mock_stream = MockStream([hello.decode("utf-8")])
    monkeypatch.setattr(
        "kubernetes.stream.stream", lambda *a, **ka: mock_stream
    )
    monkeypatch.setattr(
        "t4cclient.sessions.operators.k8s.KubernetesOperator._get_pod_name",
        lambda *a: "",
    )

    oper = KubernetesOperator()
    download_iter = oper.download_file("some-id", "filename")

    assert as_text(download_iter) == "hello"


def as_text(bytes_iter):
    return "".join(b.decode("utf-8") for b in bytes_iter)


class MockStream:
    def __init__(self, blocks):
        self._blocks = blocks

    def is_open(self):
        return bool(self._blocks)

    def read_stdout(self, timeout=None):
        return self._blocks.pop(0)
