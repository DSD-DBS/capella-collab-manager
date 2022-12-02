# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
import requests

import capellacollab.sessions.idletimeout
from capellacollab.sessions.idletimeout import terminate_idle_session


@pytest.fixture(autouse=True)
def mock_config(monkeypatch):

    monkeypatch.setattr(
        capellacollab.sessions.idletimeout,
        "config",
        {"prometheus": {"url": ""}, "requests": {"timeout": 60}},
    )


class MockResponse:
    def __init__(self, *alerts, status_code=200):
        self._alerts = alerts
        self.status_code = 200

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


def test_no_idle_sessions(monkeypatch, db):
    operator = MockOperator()
    monkeypatch.setattr(
        requests,
        "get",
        lambda *args, **kwargs: MockResponse({"metric": {"app": "12345"}}),
    )
    monkeypatch.setattr(
        capellacollab.sessions.idletimeout, "OPERATOR", operator
    )

    terminate_idle_session()

    assert "12345" in operator.killed_sessions
