# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest

from capellacollab.sessions import auth as sessions_auth
from capellacollab.sessions.hooks import authentication
from capellacollab.sessions.hooks import interface as sessions_hooks_interface


def test_pre_authentication_hook(
    session_connection_hook_request: sessions_hooks_interface.SessionConnectionHookRequest,
    monkeypatch: pytest.MonkeyPatch,
):
    private_key = sessions_auth.generate_private_key()
    monkeypatch.setattr(sessions_auth, "PRIVATE_KEY", private_key)

    result = authentication.PreAuthenticationHook().session_connection_hook(
        session_connection_hook_request
    )

    assert "ccm_session_token" in result["cookies"]
