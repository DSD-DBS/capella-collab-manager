# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging

import requests

from capellacollab import core
from capellacollab.config import config

log = logging.getLogger(__name__)


def get_last_seen(sid: str) -> str:
    """Return project session last seen activity"""
    if core.LOCAL_DEVELOPMENT_MODE:
        return "Disabled in development mode"

    url = f"{config.prometheus.url}/api/v1/query?query=idletime_minutes"
    try:
        response = requests.get(
            url,
            timeout=config.requests.timeout,
        )
        response.raise_for_status()

        for session in response.json()["data"]["result"]:
            if sid == session["metric"]["session_id"]:
                return _get_last_seen(float(session["value"][1]))

        log.debug("Couldn't find Prometheus metrics for session %s.", sid)
    except Exception:
        log.exception("Exception during fetching of last seen.")
    return "UNKNOWN"


def _get_last_seen(idletime: int | float) -> str:
    if idletime == -1:
        return "Never connected"

    if (idlehours := idletime / 60) > 1:
        return f"{round(idlehours, 2)} hrs ago"

    return f"{idletime:.0f} mins ago"
