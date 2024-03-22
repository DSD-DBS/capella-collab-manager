# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import kubernetes.config
import pytest


@pytest.fixture(autouse=True)
def mock_k8s_load_config(monkeypatch):
    monkeypatch.setattr(kubernetes.config, "load_config", lambda **_: None)
