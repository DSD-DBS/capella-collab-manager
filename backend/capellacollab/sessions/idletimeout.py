# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import logging
import os

import requests

from capellacollab import scheduling
from capellacollab.configuration.app import config
from capellacollab.core import database
from capellacollab.permissions import injectables as permissions_injectables

from . import crud, operators, util

log = logging.getLogger(__name__)


def terminate_idle_session():
    if os.getenv("DISABLE_SESSION_TIMEOUT", "") in ("true", "1", "t"):
        log.info(
            "Session timeout is disabled, skipping idle session termination."
        )
        return
    log.debug("Starting to terminate idle sessions...")
    url = config.prometheus.url
    url += "/".join(("api", "v1", 'query?query=ALERTS{alertstate="firing"}'))
    response = requests.get(
        url,
        timeout=config.requests.timeout,
    )
    log.debug("Requested alerts %d", response.status_code)
    if response.status_code != 200:
        log.error("Could not collect idle sessions from Prometheus")
        return
    for metric in response.json()["data"]["result"]:
        if session_id := metric.get("metric", {}).get("session_id"):
            log.info("Terminating idle session %s", session_id)
            with database.SessionLocal() as db:
                if session := crud.get_session_by_id(db, session_id):
                    util.terminate_session(
                        db,
                        session,
                        operators.get_operator(),
                        permissions_injectables.get_scope(session.owner, None),
                        logging.LoggerAdapter(log),
                    )
                else:
                    log.error(
                        "Session was not found in our database. Terminating idle session %s",
                        session_id,
                    )
                    operators.get_operator().kill_session(session_id)
    log.debug("Finished termination of idle sessions.")


def terminate_idle_sessions_in_background():
    scheduling.scheduler.add_job(
        terminate_idle_session,
        "interval",
        minutes=1,
        id="terminate_idle_sessions",
        replace_existing=True,
    )


def run():
    logging.basicConfig(level=config.logging.level)
    terminate_idle_session()


if __name__ == "__main__":
    run()
