# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import typing as t

import pytest
from fastapi import testclient

from capellacollab.__main__ import app
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.core.authentication import oidc_provider


class MockPyJWK:
    def __init__(self) -> None:
        self.key = "mock-key"


class MockJWKSClient:
    def get_signing_key_from_jwt(self, token: str):
        return MockPyJWK()


class MockJWTConfig:
    def __init__(
        self, oidc_config: oidc_provider.AbstractOIDCProviderConfig
    ) -> None:
        self.oidc_config = oidc_config
        self.jwks_client = MockJWKSClient()


class MockOIDCProviderConfig(oidc_provider.AbstractOIDCProviderConfig):
    def get_authorization_endpoint(self) -> str:
        return "mock-authorization-endpoint"

    def get_token_endpoint(self) -> str:
        return "mock-token-endpoint"

    def get_jwks_uri(self) -> str:
        return "mock-jwks-uri"

    def get_supported_signing_algorithms(self) -> list[str]:
        return ["RS256"]

    def get_issuer(self) -> str:
        return "mock-issuer"

    def get_scopes(self) -> list[str]:
        return ["openid", "offline_access", "email"]

    def get_client_secret(self) -> str:
        return "mock-secret"

    def get_client_id(self) -> str:
        return "mock-client-id"


class MockOIDCProvider(oidc_provider.AbstractOIDCProvider):
    def __init__(self, oidc_config: oidc_provider.AbstractOIDCProviderConfig):
        super().__init__(oidc_config)
        self.oidc_config = oidc_config

    def get_authorization_url_with_parameters(
        self,
    ) -> t.Tuple[str, str, str, str]:
        return (
            "mock-auth-url",
            "mock-state",
            "mock-nonce",
            "mock-code-verifier",
        )

    def exchange_code_for_tokens(
        self, authorization_code: str, code_verifier: str
    ) -> dict[str, t.Any]:
        return {
            "id_token": "mock-id-token",
            "access-token": "mock-access-token",
            "refresh-token": "mock-refresh-token",
        }

    def refresh_token(self, _refresh_token: str) -> dict[str, t.Any]:
        return {
            "id_token": "mock-id-token",
            "access-token": "mock-access-token",
            "refresh-token": "mock-refresh-token",
        }


@pytest.fixture(name="mock_oidc_provider_and_config")
def fixture_mock_oidc_provider_and_config(
    mock_oidc_config: oidc_provider.AbstractOIDCProviderConfig,
    mock_oidc_provider: oidc_provider.AbstractOIDCProvider,
):
    async def get_mock_oidc_config() -> (
        oidc_provider.AbstractOIDCProviderConfig
    ):
        return mock_oidc_config

    async def get_mock_oidc_provider() -> oidc_provider.AbstractOIDCProvider:
        return mock_oidc_provider

    app.dependency_overrides[auth_injectables.get_oidc_config] = (
        get_mock_oidc_config
    )
    app.dependency_overrides[auth_injectables.get_oidc_provider] = (
        get_mock_oidc_provider
    )

    yield

    del app.dependency_overrides[auth_injectables.get_oidc_config]
    del app.dependency_overrides[auth_injectables.get_oidc_provider]


@pytest.mark.usefixtures("mock_oidc_provider_and_config")
@pytest.fixture(name="unauthorized_client")
def fixture_unauthorized_client(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        "capellacollab.core.authentication.api_key_cookie.JWTConfig",
        MockJWTConfig,
    )
    return testclient.TestClient(app)
