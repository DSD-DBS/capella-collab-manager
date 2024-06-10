# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


from unittest import mock

import pytest
from fastapi import status, testclient
from sqlalchemy import orm

from capellacollab.core.authentication import (
    api_key_cookie,
    exceptions,
    flow,
    routes,
)


@pytest.fixture(name="mock_auth_endpoints")
def fixture_mock_auth_endpoints(monkeypatch: pytest.MonkeyPatch):
    def mock_get_auth_endpoints() -> flow.AuthEndpoints:
        return {
            "authorization_endpoint": "https://pytest.mock/authorize",
            "token_endpoint": "https://pytest.mock/token",
            "jwks_uri": "https://pytest.mock/jwks_uri",
        }

    monkeypatch.setattr(flow, "get_auth_endpoints", mock_get_auth_endpoints)


@pytest.mark.usefixtures("mock_auth_endpoints")
def test_get_authorization_url_with_parameters(
    monkeypatch: pytest.MonkeyPatch,
):
    mock_generate_token = mock.Mock(return_value="mock-token")
    monkeypatch.setattr("oauthlib.common.generate_token", mock_generate_token)

    mock_generate_nonce = mock.Mock(return_value="mock-nonce")
    monkeypatch.setattr("oauthlib.common.generate_nonce", mock_generate_nonce)

    monkeypatch.setattr(
        flow.auth_config, "redirect_uri", "https://pytest.mock/callback"
    )
    monkeypatch.setattr(flow.web_client, "client_id", "mock-clientID")
    monkeypatch.setattr(flow.auth_config, "scopes", ["openid", "profile"])

    auth_url, state, nonce, _ = flow.get_authorization_url_with_parameters()

    assert "https://pytest.mock/authorize" in auth_url
    assert "response_type=code" in auth_url
    assert "client_id=mock-clientID" in auth_url
    assert "redirect_uri=https%3A%2F%2Fpytest.mock%2Fcallback" in auth_url
    assert state == "mock-token"
    assert "state=mock-token" in auth_url
    assert nonce == "mock-nonce"
    assert "nonce=mock-nonce" in auth_url
    assert "code_challenge" in auth_url
    assert f"code_challenge_method={flow.CODE_CHALLENGE_METHOD}" in auth_url


def test_get_redirect_url(
    unauthorized_client: testclient.TestClient, monkeypatch: pytest.MonkeyPatch
):
    def mock_get_authorization_url_with_parameters():
        return (
            "mock-auth_url",
            "mock-state",
            "mock-nonce",
            "mock-code_verifier",
        )

    monkeypatch.setattr(
        flow,
        "get_authorization_url_with_parameters",
        mock_get_authorization_url_with_parameters,
    )

    response = unauthorized_client.get("api/v1/authentication")
    json_response = response.json()

    cookies = "".join(response.headers.get_list("set-cookie"))

    assert response.status_code == 200
    assert "auth_url" in json_response
    assert "state" in json_response
    assert "nonce" in json_response
    assert "code_verifier" in json_response

    assert 'id_token=""' in cookies
    assert 'refresh_token=""' in cookies


def test_missing_refresh_token(unauthorized_client: testclient.TestClient):
    response = unauthorized_client.put("api/v1/authentication/tokens")
    json_response = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json_response["detail"]["err_code"] == "NO_REFRESH_TOKEN_COOKIE"


@pytest.mark.usefixtures("mock_auth_endpoints")
def test_validate_id_token_nonce_mismatch(
    db: orm.Session, monkeypatch: pytest.MonkeyPatch
):
    mock_jwt_api_cookie = mock.MagicMock()
    mock_jwt_api_cookie.return_value.validate_token.return_value = {
        "nonce": "mismatch-nonce"
    }

    monkeypatch.setattr(api_key_cookie, "JWTAPIKeyCookie", mock_jwt_api_cookie)

    with pytest.raises(exceptions.NonceMismatchError):
        routes.validate_id_token(db, "any", "correct-nonce")


@pytest.mark.usefixtures("mock_auth_endpoints")
def test_validate_id_token_audience_mismatch(
    db: orm.Session, monkeypatch: pytest.MonkeyPatch
):
    mock_jwt_api_cookie = mock.MagicMock()
    mock_jwt_api_cookie.return_value.validate_token.return_value = {
        "nonce": "mock-nonce",
        "aud": "mock-audience",
    }

    monkeypatch.setattr(api_key_cookie, "JWTAPIKeyCookie", mock_jwt_api_cookie)
    monkeypatch.setattr(flow.auth_config.client, "id", "mismatch-clientId")

    with pytest.raises(exceptions.UnauthenticatedError):
        routes.validate_id_token(db, "any", "mock-nonce")
