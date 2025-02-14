# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging

import requests

from capellacollab import core
from capellacollab.configuration.app import config
from capellacollab.sessions import models2 as sessions_models2

log = logging.getLogger(__name__)


def get_idle_state(sid: str) -> sessions_models2.IdleState:
    if core.LOCAL_DEVELOPMENT_MODE:
        return sessions_models2.IdleState(
            available=False,
            unavailable_reason="Unavailable in local development mode",
            terminate_after_minutes=config.sessions.timeout,
        )

    try:
        response = requests.get(
            f'{config.prometheus.url}/api/v1/query?query=idletime_minutes{{session_id="{sid}"}}',
            timeout=config.requests.timeout,
        )
        response.raise_for_status()
    except Exception:
        log.exception("Exception during fetching of idle state.")
        return sessions_models2.IdleState(
            available=False,
            unavailable_reason="Exception during fetching of idle state",
            terminate_after_minutes=config.sessions.timeout,
        )

    if len(response.json()["data"]["result"]) > 0:
        idle_for_minutes = int(
            float(response.json()["data"]["result"][0]["value"][1])
        )
        return sessions_models2.IdleState(
            available=True,
            idle_for_minutes=idle_for_minutes,
            terminate_after_minutes=config.sessions.timeout,
        )
    log.debug("Couldn't find Prometheus metrics for session %s.", sid)

    return sessions_models2.IdleState(
        available=False,
        unavailable_reason="No metrics found for session",
        terminate_after_minutes=config.sessions.timeout,
    )
