# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest

from capellacollab.sessions import auth as sessions_auth
from capellacollab.sessions import models as sessions_models
from capellacollab.sessions.hooks import http
from capellacollab.sessions.hooks import interface as sessions_hooks_interface
from capellacollab.tools import models as tools_models


def test_http_hook(
    session: sessions_models.DatabaseSession,
    session_connection_hook_request: sessions_hooks_interface.SessionConnectionHookRequest,
):
    session.environment = {
        "TEST": "test",
        "CAPELLACOLLAB_SESSION_TOKEN": "test",
    }
    connection_method = tools_models.HTTPConnectionMethod(
        redirect_url="http://localhost:8000/{TEST}",
        cookies={"test": "{TEST}"},
    )
    session_connection_hook_request.connection_method = connection_method
    session_connection_hook_request.db_session = session
    result = http.HTTPIntegration().session_connection_hook(
        session_connection_hook_request
    )

    assert result["cookies"]["test"] == "test"
    assert result["redirect_url"] == "http://localhost:8000/test"
    assert not result["warnings"]


def test_skip_http_hook_if_guacamole(
    session_connection_hook_request: sessions_hooks_interface.SessionConnectionHookRequest,
):
    result = http.HTTPIntegration().session_connection_hook(
        session_connection_hook_request
    )
    assert len(result) == 1
    assert len(result["cookies"]) == 1


def test_fail_derive_redirect_url(
    session: sessions_models.DatabaseSession,
    session_connection_hook_request: sessions_hooks_interface.SessionConnectionHookRequest,
):
    session.environment = {"TEST": "test"}
    connection_method = tools_models.HTTPConnectionMethod(
        redirect_url="http://localhost:8000/{TEST2}"
    )
    session_connection_hook_request.connection_method = connection_method
    session_connection_hook_request.db_session = session
    result = http.HTTPIntegration().session_connection_hook(
        session_connection_hook_request
    )

    assert len(result["warnings"]) == 1
    assert result["warnings"][0].err_code == "REDIRECT_URL_DERIVATION_FAILED"


def test_pre_auth_cookie(
    session_connection_hook_request: sessions_hooks_interface.SessionConnectionHookRequest,
    monkeypatch: pytest.MonkeyPatch,
):
    private_key = sessions_auth.generate_private_key()
    monkeypatch.setattr(sessions_auth, "PRIVATE_KEY", private_key)

    result = http.HTTPIntegration().session_connection_hook(
        session_connection_hook_request
    )

    assert "ccm_session_token" in result["cookies"]
