# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import logging

import click
from t4cclient.core import database
from t4cclient.core.database import sessions
from t4cclient.routes.sessions import inject_attrs_in_sessions

LOGGER = logging.getLogger(__name__)


@click.command()
def clean_old_sessions():
    with database.SessionLocal() as db:
        for session in inject_attrs_in_sessions(sessions.get_all_sessions(db)):
            if session["state"] == "exited":
                try:
                    sessions.delete_session(db, session["id"])
                except Exception as e:
                    LOGGER.info(
                        "Removing then container with id %s failed",
                        session["id"],
                        exc_info=True,
                    )


if __name__ == "__main__":
    clean_old_sessions()
