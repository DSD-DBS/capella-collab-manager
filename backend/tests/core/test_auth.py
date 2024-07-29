# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


from unittest import mock

import pytest
from fastapi import status, testclient

from capellacollab.core.authentication import (
    api_key_cookie,
    exceptions,
    oidc_provider,
    routes,
)


def test_missing_refresh_token(unauthorized_client: testclient.TestClient):
    response = unauthorized_client.put("api/v1/authentication/tokens")
    json_response = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json_response["detail"]["err_code"] == "NO_REFRESH_TOKEN_COOKIE"


@pytest.mark.usefixtures("mock_auth_endpoints")
def test_validate_id_token_nonce_mismatch(
    mock_oidc_config: oidc_provider.AbstractOIDCProviderConfig,
    monkeypatch: pytest.MonkeyPatch,
):
    mock_jwt_api_cookie = mock.MagicMock()
    mock_jwt_api_cookie.return_value.validate_token.return_value = {
        "nonce": "mismatch-nonce"
    }

    monkeypatch.setattr(api_key_cookie, "JWTAPIKeyCookie", mock_jwt_api_cookie)

    with pytest.raises(exceptions.NonceMismatchError):
        routes.validate_id_token("any", mock_oidc_config, "correct-nonce")


@pytest.mark.usefixtures("mock_auth_endpoints")
def test_validate_id_token_audience_mismatch(
    mock_oidc_config: oidc_provider.AbstractOIDCProviderConfig,
    monkeypatch: pytest.MonkeyPatch,
):
    mock_jwt_api_cookie = mock.MagicMock()
    mock_jwt_api_cookie.return_value.validate_token.return_value = {
        "nonce": "mock-nonce",
        "aud": "mock-audience",
    }

    monkeypatch.setattr(api_key_cookie, "JWTAPIKeyCookie", mock_jwt_api_cookie)

    with pytest.raises(exceptions.UnauthenticatedError):
        routes.validate_id_token("any", mock_oidc_config, "mock-nonce")
