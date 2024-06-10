# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import pytest
from fastapi import testclient

from capellacollab.__main__ import app


class MockPyJWK:
    def __init__(self) -> None:
        self.key = "mock-key"


class MockJWKSClient:
    def get_signing_key_from_jwt(self, token: str):
        return MockPyJWK()


class MockJWTConfigBorg:
    _shared_state: dict[str, str] = {}

    def __init__(self) -> None:
        self.__dict__ = self._shared_state

        if not hasattr(self, "_jwks_client"):
            self.jwks_client = MockJWKSClient()

        if not hasattr(self, "_supported_signing_algorithms"):
            self.supported_signing_algorithms = ["RS256"]


@pytest.fixture(name="unauthorized_client")
def fixture_unauthorized_client(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        "capellacollab.core.authentication.api_key_cookie.JWTConfigBorg",
        MockJWTConfigBorg,
    )

    return testclient.TestClient(app)
