# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest

from capellacollab import core
from capellacollab.sessions import injection


def test_get_last_seen_disabled_in_development_mode(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(core, "LOCAL_DEVELOPMENT_MODE", True)
    assert injection.get_last_seen("test") == "Disabled in development mode"
