# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import asyncio

import pytest

from capellacollab.settings.modelsources.git import core as instances_git_core


@pytest.fixture(name="mock_ls_remote")
def fixture_mock_ls_remote(
    monkeypatch: pytest.MonkeyPatch,
):
    ls_remote = (
        "0665eb5bf5dc3a7bdcb30b4354c85eddde2bd847	HEAD\n"
        "e0f83d8d57ec1552c5fb76c83f7dff7f0ff86631	refs/heads/test-branch1\n"
        "76c71f5468f6e444317146c6c9a3e00033974a1c	refs/heads/test-branch2\n"
        "0665eb5bf5dc3a7bdcb30b4354c85eddde2bd847	refs/heads/main\n"
        "ea10a5a82f31807d89c1bb7fc61dcd331e49f8fc	refs/pull/100/head\n"
        "47cda65668eb258c5e84a8ffd43909ba4fac2661	refs/tags/v1.0.0\n"
        "bce139e467d3d60bd21a4097c78e86a87e1a5d21	refs/tags/v1.1.0\n"
    )

    # pylint: disable=unused-argument
    def mock_ls_remote(*args, **kwargs):
        f: asyncio.Future = asyncio.Future()
        f.set_result(ls_remote)
        return f

    monkeypatch.setattr(
        instances_git_core, "_ls_remote_command", mock_ls_remote
    )
