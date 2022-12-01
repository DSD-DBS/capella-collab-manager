# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import logging

import requests

from capellacollab.config import config
from capellacollab.core.database import SessionLocal
from capellacollab.sessions import database
from capellacollab.sessions.operators import OPERATOR

log = logging.getLogger(__name__)


def terminate_idle_session():
    url = config["prometheus"]["url"]
    url += "/".join(("api", "v1", 'query?query=ALERTS{alertstate="firing"}'))
    response = requests.get(
        url,
        timeout=config["requests"]["timeout"],
    )
    log.info("Requested alerts %d", response.status_code)
    for metric in response.json()["data"]["result"]:
        if session_id := metric.get("metric", {}).get("app"):
            log.info("Terminating idle session %s", session_id)
            OPERATOR.kill_session(session_id)
            with SessionLocal() as db:
                if session := database.get_session_by_id(db, session_id):
                    database.delete_session(db, session)


def run():
    logging.basicConfig(level=config["logging"]["level"])
    terminate_idle_session()


if __name__ == "__main__":
    run()
