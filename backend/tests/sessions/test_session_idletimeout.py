# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
import requests

import capellacollab.sessions.idletimeout
from capellacollab.config import models as config_models
from capellacollab.sessions.idletimeout import terminate_idle_session


@pytest.fixture(autouse=True)
def mock_config(monkeypatch):
    mocked_config = config_models.AppConfig(
        prometheus=config_models.PrometheusConfig(url=""),
        requests=config_models.RequestsConfig(timeout=60),
    )
    monkeypatch.setattr(
        capellacollab.sessions.idletimeout, "config", mocked_config
    )


class MockResponse:
    def __init__(self, *alerts, status_code=200):
        self._alerts = alerts
        self.status_code = status_code

    def json(self):
        return {"data": {"result": self._alerts}}


class MockOperator:
    def __init__(self):
        self.killed_sessions = []

    def kill_session(self, session_id):
        self.killed_sessions.append(session_id)


def test_no_idle_sessions(monkeypatch):
    monkeypatch.setattr(
        requests, "get", lambda *args, **kwargs: MockResponse()
    )

    terminate_idle_session()


@pytest.mark.usefixtures("db")
def test_idle_sessions(monkeypatch):
    session_id: str = "12345"

    operator = MockOperator()
    monkeypatch.setattr(
        requests,
        "get",
        lambda *args, **kwargs: MockResponse({"metric": {"app": session_id}}),
    )
    monkeypatch.setattr(
        capellacollab.sessions.operators,
        "get_operator",
        lambda: operator,
    )

    terminate_idle_session()

    assert session_id in operator.killed_sessions
