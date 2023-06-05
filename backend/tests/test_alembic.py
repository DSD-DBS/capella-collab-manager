# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import pathlib
import time

import docker
import docker.models.containers
import pytest
import sqlalchemy
from alembic import command
from alembic.config import Config

from capellacollab.core.database import migration

database_connect_timeout = 60  # in seconds
log = logging.getLogger(__file__)
log.setLevel("DEBUG")
client = docker.from_env()


@pytest.fixture(name="docker_database")
def fixture_docker_database():
    log.info("Start database")
    container = client.containers.run(
        image="postgres",
        environment={
            "POSTGRES_PASSWORD": "dev",
            "POSTGRES_USER": "dev",
            "POSTGRES_DB": "dev",
        },
        volumes={
            str(pathlib.Path(__file__).parent / "data" / "database"): {
                "bind": "/tmp/sql",
                "mode": "ro",
            }
        },
        remove=True,
        detach=True,
        ports={"5432/tcp": None},
    )

    yield container

    container.stop()


@pytest.fixture(name="alembic_revision", params=["687484695147"])
def fixture_alembic_revision(request) -> str:
    return request.param


@pytest.fixture(name="initialized_database")
def fixture_initialized_database(
    docker_database: docker.models.containers.Container, alembic_revision: str
):
    docker_database.reload()
    port = docker_database.ports["5432/tcp"][0]["HostPort"]
    for _ in range(int(database_connect_timeout / 2)):
        log.debug("Wait until database accepts connections")
        output = docker_database.exec_run(
            cmd="pg_isready -h 'localhost' -p 5432 -U dev -d dev"
        )
        if output.exit_code == 0:
            log.info("Database is ready and accepts connections")
            break

        time.sleep(2)
    else:
        raise TimeoutError("Database connection timed out")

    output = docker_database.exec_run(
        cmd=f"psql -h 'localhost' -p 5432 -U dev dev -f /tmp/sql/{alembic_revision}.sql"
    )
    if output.exit_code == 0:
        log.debug(output.output.decode())
    else:
        raise RuntimeError(output.output.decode())

    yield sqlalchemy.create_engine(
        f"postgresql://dev:dev@localhost:{port}/dev"
    )


@pytest.fixture(name="alembic_cfg")
def fixture_alembic_cfg(initialized_database):
    root_dir = pathlib.Path(__file__).parents[1] / "capellacollab"
    alembic_cfg = Config(root_dir / "alembic.ini")
    alembic_cfg.set_main_option("script_location", str(root_dir / "alembic"))
    alembic_cfg.set_main_option(
        "sqlalchemy.url", str(initialized_database.url)
    )
    alembic_cfg.attributes["configure_logger"] = False
    yield alembic_cfg


def test_init_database(
    initialized_database, alembic_cfg, alembic_revision: str
):
    # Update database to HEAD
    migration.migrate_db(
        initialized_database,
        str(initialized_database.url).replace("***", "dev"),
    )
