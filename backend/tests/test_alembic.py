# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import pathlib

import docker
import docker.models.containers
import pytest
import sqlalchemy
from _pytest.monkeypatch import MonkeyPatch
from alembic import command
from alembic.config import Config
from testcontainers.postgres import PostgresContainer

import capellacollab.sql_models
from capellacollab.core.database import migration

log = logging.getLogger(__file__)
log.setLevel("DEBUG")
client = docker.from_env()


@pytest.fixture()
def docker_database():
    log.info("Start database")
    container = client.containers.run(
        image="postgres",
        environment={
            "POSTGRES_PASSWORD": "dev",
            "POSTGRES_USER": "dev",
            "POSTGRES_DB": "dev",
        },
        volumes={
            str(pathlib.Path(__file__).parents[1] / "data" / "database"): {
                "bind": "/tmp/sql",
                "mode": "ro",
            }
        },
        remove=True,
        detach=True,
        ports={"5432/tcp": "5432-6000"},
    )

    yield container

    container.stop()


@pytest.fixture(params=["687484695147.sql"])
def initialized_database(
    docker_database: docker.models.containers.Container, request
):
    docker_database.exec_run(
        cmd=f"psql -h 'localhost' -p 5432 -U dev dev -f /tmp/database/{request.param}"
    )

    yield sqlalchemy.create_engine("postgresql://dev:dev@localhost:5432/dev")


@pytest.fixture()
def alembic_cfg(initialized_database):
    root_dir = pathlib.Path(__file__).parents[1] / "capellacollab"
    alembic_cfg = Config(root_dir / "alembic.ini")
    alembic_cfg.set_main_option("script_location", str(root_dir / "alembic"))
    alembic_cfg.set_main_option(
        "sqlalchemy.url", str(initialized_database.url)
    )
    alembic_cfg.attributes["configure_logger"] = False
    yield alembic_cfg


def test_init_database(
    initialized_database, alembic_cfg, monkeypatch: MonkeyPatch
):
    # Update database to HEAD
    migration.migrate_db(initialized_database)

    # Downgrade database to 687484695147
    command.downgrade(alembic_cfg, "687484695147")

    # And migrate to HEAD again
    migration.migrate_db(initialized_database)
