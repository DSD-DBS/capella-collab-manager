# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import asyncio
import logging

import requests
from starlette.concurrency import run_in_threadpool

from capellacollab.config import config
from capellacollab.core import database
from capellacollab.sessions import routes
from capellacollab.sessions.database import get_session_by_id
from capellacollab.sessions.operators import OPERATOR

log = logging.getLogger(__name__)


def terminate_idle_session():
    url = config["prometheus"]["url"]
    url += "/".join(("api", "v1", 'query?query=ALERTS{alertstate="firing"}'))
    response = requests.get(
        url,
        timeout=config["requests"]["timeout"],
    )
    log.debug("Requested alerts %d", response.status_code)
    if response.status_code != 200:
        log.error("Could not collect idle sessions from Prometheus")
        return
    for metric in response.json()["data"]["result"]:
        if session_id := metric.get("metric", {}).get("app"):
            log.info("Terminating idle session %s", session_id)
            with database.SessionLocal() as db:
                if session := get_session_by_id(db, session_id):
                    routes.end_session(session, db, OPERATOR)
                else:
                    log.error(
                        "Session was not found in our database. Terminating idle session %s",
                        session_id,
                    )
                    OPERATOR.kill_session(session_id)


async def terminate_idle_sessions_in_background(interval=60):
    async def loop():
        while True:
            try:
                await asyncio.sleep(interval)
                await run_in_threadpool(terminate_idle_session)
            except BaseException:
                log.exception("Could not handle idle sessions")

    asyncio.ensure_future(loop())


def run():
    logging.basicConfig(level=config["logging"]["level"])
    terminate_idle_session()


if __name__ == "__main__":
    run()
