# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
import responses
from fastapi import status

from capellacollab import core
from capellacollab.config import config
from capellacollab.sessions import injection
from capellacollab.sessions import models2 as models2_sessions


def test_get_idle_status_disabled_in_development_mode(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(core, "LOCAL_DEVELOPMENT_MODE", True)
    assert injection.get_idle_state("test") == models2_sessions.IdleState(
        available=False,
        terminate_after_minutes=90,
        unavailable_reason="Unavailable in local development mode",
    )


def test_get_idle_status_exception():
    assert injection.get_idle_state("test") == models2_sessions.IdleState(
        available=False,
        unavailable_reason="Exception during fetching of idle state",
        terminate_after_minutes=90,
    )


def test_get_idle_status_unknown_session():
    with responses.RequestsMock() as rsps:
        rsps.get(
            f'{config.prometheus.url}/api/v1/query?query=idletime_minutes{{session_id="test"}}',
            status=status.HTTP_200_OK,
            json={
                "status": "success",
                "data": {"resultType": "vector", "result": []},
            },
        )

        assert injection.get_idle_state("test") == models2_sessions.IdleState(
            available=False,
            unavailable_reason="No metrics found for session",
            terminate_after_minutes=90,
        )


def test_get_idle_status():
    with responses.RequestsMock() as rsps:
        rsps.get(
            f'{config.prometheus.url}/api/v1/query?query=idletime_minutes{{session_id="test"}}',
            status=status.HTTP_200_OK,
            json={
                "status": "success",
                "data": {
                    "resultType": "vector",
                    "result": [
                        {
                            "value": [1731683497.386, "12.5"],
                        }
                    ],
                },
            },
        )

        assert injection.get_idle_state("test") == models2_sessions.IdleState(
            available=True,
            idle_for_minutes=12,
            terminate_after_minutes=90,
        )
