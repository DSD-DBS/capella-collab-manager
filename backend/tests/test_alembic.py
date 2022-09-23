# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import logging

import docker
import pytest
from _pytest.monkeypatch import MonkeyPatch

import capellacollab.sql_models
from capellacollab.core.database import __main__ as core_database

log = logging.getLogger(__file__)
log.setLevel("DEBUG")
client = docker.from_env()


@pytest.fixture()
def database():
    log.info("Start database")
    container = client.containers.run(
        image="postgres",
        environment={
            "POSTGRES_PASSWORD": "dev",
            "POSTGRES_USER": "dev",
            "POSTGRES_DB": "dev",
        },
        remove=True,
        detach=True,
        network_mode="host",
    )
    log.info("Started database")

    yield "postgresql://dev:dev@localhost:5432/dev"

    print("Stop database")
    container.stop()


def test_init_database(database, monkeypatch: MonkeyPatch):
    core_database.DATABASE_URL = database
    core_database.migrate_db()
