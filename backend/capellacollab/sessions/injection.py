# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import re

import requests

from capellacollab import core
from capellacollab.config import config

from . import operators

log = logging.getLogger(__name__)


def get_last_seen(sid: str) -> str:
    """Return project session last seen activity"""
    if core.DEVELOPMENT_MODE:
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


def determine_session_state(session_id: str) -> str:
    state = operators.get_operator().get_session_state(session_id)

    if state in ("Started", "BackOff"):
        try:
            logs = operators.get_operator().get_session_logs(
                session_id, container="session-preparation"
            )
            logs += operators.get_operator().get_session_logs(session_id)
            res = re.search(r"(?s:.*)^---(.*?)---$", logs, re.MULTILINE)
            if res:
                return res.group(1)
        except Exception:
            log.exception("Could not parse log")
    return state
