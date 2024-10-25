# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from fastapi import testclient

from capellacollab.sessions import auth as sessions_auth
from capellacollab.sessions import models as sessions_models
from capellacollab.sessions.hooks import (
    authentication as sessions_authentication_hook,
)
from capellacollab.users import models as users_models


@pytest.fixture(name="session_token")
def fixture_session_token(
    monkeypatch: pytest.MonkeyPatch,
    session: sessions_models.DatabaseSession,
    user: users_models.DatabaseUser,
) -> str:
    private_key = sessions_auth.generate_private_key()
    monkeypatch.setattr(sessions_auth, "PRIVATE_KEY", private_key)
    monkeypatch.setattr(sessions_auth, "PUBLIC_KEY", private_key.public_key())

    return sessions_authentication_hook.PreAuthenticationHook()._issue_session_token(
        user=user, db_session=session
    )


def test_validate_session_token_with_invalid_session(
    client: testclient.TestClient,
    session_token: str,
):
    """Test that it's not possible to see if a session is running with an invalid token"""

    response = client.post(
        "/api/v1/sessions/xwmuiapqqnwxlmcpchsifnamj/tokens/validate",
        cookies={
            "ccm_session_token": session_token,
        },
    )

    assert response.status_code == 403


def test_validate_session_token_without_token_cookie(
    client: testclient.TestClient,
    session: sessions_models.DatabaseSession,
):
    """Test that a request without a cookie is declined during validation"""

    response = client.post(f"/api/v1/sessions/{session.id}/tokens/validate")

    assert response.status_code == 401


@pytest.mark.usefixtures("session_token")
def test_validate_session_token_with_invalid_token(
    client: testclient.TestClient,
    session: sessions_models.DatabaseSession,
):
    """Test that an invalid token is declined during validation"""

    response = client.post(
        f"/api/v1/sessions/{session.id}/tokens/validate",
        cookies={"ccm_session_token": "invalid"},
    )

    assert response.status_code == 401


def test_validate_session_token_with_valid_token(
    client: testclient.TestClient,
    session: sessions_models.DatabaseSession,
    session_token: str,
):
    """Test that a valid session tokens also validates correctly"""

    response = client.post(
        f"/api/v1/sessions/{session.id}/tokens/validate",
        cookies={
            "ccm_session_token": session_token,
        },
    )

    assert response.is_success


def test_validate_session_token_with_invalid_signature(
    client: testclient.TestClient,
    monkeypatch: pytest.MonkeyPatch,
    session: sessions_models.DatabaseSession,
    user: users_models.DatabaseUser,
):
    """Test that the token validation fails if the signature is invalid"""

    private_key = sessions_auth.generate_private_key()
    monkeypatch.setattr(sessions_auth, "PRIVATE_KEY", private_key)

    another_private_key = sessions_auth.generate_private_key()
    monkeypatch.setattr(
        sessions_auth, "PUBLIC_KEY", another_private_key.public_key()
    )

    token = sessions_authentication_hook.PreAuthenticationHook()._issue_session_token(
        user=user, db_session=session
    )

    response = client.post(
        f"/api/v1/sessions/{session.id}/tokens/validate",
        cookies={
            "ccm_session_token": token,
        },
    )

    assert response.status_code == 401
