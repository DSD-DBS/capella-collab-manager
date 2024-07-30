# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


from unittest import mock

import pytest
import responses
from fastapi import status, testclient
from sqlalchemy import orm

from capellacollab.config import config
from capellacollab.core.authentication import api_key_cookie, exceptions, oidc
from capellacollab.core.authentication import routes
from capellacollab.core.authentication import routes as auth_routes
from capellacollab.users import crud as users_crud
from capellacollab.users import models as users_models


@pytest.fixture(name="mock_auth_endpoints")
def fixture_mock_oidc_endpoints(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        config.authentication.endpoints,
        "well_known",
        "https://mock.localhost/default/.well-known/openid-configuration",
    )
    responses.get(
        "https://mock.localhost/default/.well-known/openid-configuration",
        status=200,
        json={
            "authorization_endpoint": "https://mock.localhost/default/authorize",
            "token_endpoint": "https://mock.localhost/default/token",
            "jwks_uri": "https:///mock.localhost/default/jwks",
        },
    )


@pytest.fixture(name="mock_token_creation")
def fixture_mock_token_creation(monkeypatch: pytest.MonkeyPatch):
    responses.post(
        "https://mock.localhost/default/token",
        status=200,
        json={
            "id_token": "id_token",
            "refresh_token": "refresh_token",
            "access_token": "access_token",
        },
    )

    monkeypatch.setattr(config.authentication.client, "id", "client_id")
    monkeypatch.setattr(
        api_key_cookie.JWTAPIKeyCookie,
        "validate_token",
        lambda self, token: {
            "nonce": "nonce",
            "aud": "client_id",
            "sub": "sub",
        },
    )


@responses.activate
@pytest.mark.usefixtures("mock_auth_endpoints")
def test_get_prefilled_authorization_url(
    client_unauthenticated: testclient.TestClient,
):
    """Get the authorization URL from the backend"""
    response = client_unauthenticated.get("/api/v1/authentication")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["auth_url"].startswith(
        "https://mock.localhost/default/authorize"
    )


@responses.activate
@pytest.mark.usefixtures("mock_auth_endpoints", "mock_token_creation")
def test_get_identity_token(
    client_unauthenticated: testclient.TestClient,
):
    """Check that the identity token is set as cookie"""
    response = client_unauthenticated.post(
        "/api/v1/authentication/tokens",
        json={"code": "any", "nonce": "nonce", "code_verifier": "any"},
    )

    assert response.status_code == status.HTTP_200_OK

    assert "id_token" in response.headers["set-cookie"]
    assert "refresh_token" in response.headers["set-cookie"]


@responses.activate
@pytest.mark.usefixtures("mock_auth_endpoints")
def test_user_info_updated_on_login(
    db: orm.Session,
    monkeypatch: pytest.MonkeyPatch,
    client_unauthenticated: testclient.TestClient,
    user: users_models.DatabaseUser,
):
    """Propagate changes of the name or email fields of the JWT"""
    monkeypatch.setattr(
        oidc.OIDCProvider,
        "exchange_code_for_tokens",
        lambda *args: {"id_token": ""},
    )
    monkeypatch.setattr(
        config.authentication.mapping, "identifier", "idp_identifier"
    )
    monkeypatch.setattr(
        auth_routes,
        "validate_id_token",
        lambda *args: {
            "idp_identifier": user.idp_identifier,
            "sub": "new_name",
            "email": "test@example.com",
        },
    )

    response = client_unauthenticated.post(
        "/api/v1/authentication/tokens",
        json={"code": "any", "nonce": "nonce", "code_verifier": "any"},
    )
    assert response.status_code == status.HTTP_200_OK

    updated_user = users_crud.get_user_by_idp_identifier(
        db, user.idp_identifier
    )
    assert updated_user is not None
    assert updated_user.name == "new_name"
    assert updated_user.email == "test@example.com"


@responses.activate
@pytest.mark.usefixtures("mock_auth_endpoints")
def test_user_created_on_first_login(
    db: orm.Session,
    monkeypatch: pytest.MonkeyPatch,
    client_unauthenticated: testclient.TestClient,
):
    """When a user logs in the first time, it should be created"""
    assert users_crud.get_user_by_idp_identifier(db, "test") is None

    monkeypatch.setattr(
        oidc.OIDCProvider,
        "exchange_code_for_tokens",
        lambda *args: {"id_token": ""},
    )
    monkeypatch.setattr(
        auth_routes, "validate_id_token", lambda *args: {"sub": "sub"}
    )
    monkeypatch.setattr(
        auth_routes,
        "validate_id_token",
        lambda *args: {
            "sub": "test",
        },
    )

    response = client_unauthenticated.post(
        "/api/v1/authentication/tokens",
        json={"code": "any", "nonce": "nonce", "code_verifier": "any"},
    )
    assert response.status_code == status.HTTP_200_OK

    assert users_crud.get_user_by_name(db, "test") is not None


@responses.activate
@pytest.mark.usefixtures("mock_auth_endpoints", "mock_token_creation")
def test_refresh_token(
    client_unauthenticated: testclient.TestClient,
):
    response = client_unauthenticated.put(
        "/api/v1/authentication/tokens",
        cookies={
            "refresh_token": "refresh_token",
        },
        json={"code": "any", "nonce": "nonce", "code_verifier": "any"},
    )

    assert response.status_code == status.HTTP_200_OK

    assert "id_token" in response.headers["set-cookie"]
    assert "refresh_token" in response.headers["set-cookie"]


@responses.activate
@pytest.mark.usefixtures("mock_auth_endpoints")
def test_delete_token_cookies(
    client_unauthenticated: testclient.TestClient,
):
    response = client_unauthenticated.delete("/api/v1/authentication/tokens")

    assert response.status_code == status.HTTP_200_OK
    assert 'id_token=""' in response.headers["set-cookie"]


def test_missing_refresh_token(client_unauthenticated: testclient.TestClient):
    response = client_unauthenticated.put("api/v1/authentication/tokens")
    json_response = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json_response["detail"]["err_code"] == "NO_REFRESH_TOKEN_COOKIE"


@responses.activate
@pytest.mark.usefixtures("mock_auth_endpoints")
def test_validate_id_token_nonce_mismatch(
    monkeypatch: pytest.MonkeyPatch,
):
    mock_jwt_api_cookie = mock.MagicMock()
    mock_jwt_api_cookie.return_value.validate_token.return_value = {
        "nonce": "mismatch-nonce"
    }

    monkeypatch.setattr(api_key_cookie, "JWTAPIKeyCookie", mock_jwt_api_cookie)

    with pytest.raises(exceptions.NonceMismatchError):
        routes.validate_id_token("any", "correct-nonce")


@responses.activate
@pytest.mark.usefixtures("mock_auth_endpoints")
def test_validate_id_token_audience_mismatch(
    monkeypatch: pytest.MonkeyPatch,
):
    mock_jwt_api_cookie = mock.MagicMock()
    mock_jwt_api_cookie.return_value.validate_token.return_value = {
        "nonce": "mock-nonce",
        "aud": "mock-audience",
    }

    monkeypatch.setattr(api_key_cookie, "JWTAPIKeyCookie", mock_jwt_api_cookie)

    with pytest.raises(exceptions.UnauthenticatedError):
        routes.validate_id_token("any", "mock-nonce")
