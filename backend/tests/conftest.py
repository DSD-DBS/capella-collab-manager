# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import base64
import datetime
import logging
import os
import pathlib
import typing as t

import aioresponses
import jwt
import pytest
import sqlalchemy
from apscheduler.jobstores import memory as ap_memory
from apscheduler.schedulers import background as ap_background_scheduler
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import testclient
from sqlalchemy import engine, orm
from testcontainers import postgres

from capellacollab import scheduling
from capellacollab.__main__ import app
from capellacollab.core import database
from capellacollab.core.database import migration
from capellacollab.users import models as users_models

os.environ["DEVELOPMENT_MODE"] = "1"


def transform_file_path_to_python_module_string(
    file_path: pathlib.Path,
) -> str:
    return (
        str(file_path.relative_to(pathlib.Path(__file__).parent))
        .replace(os.sep, ".")
        .replace(".py", "")
    )


def get_all_fixtures():
    """Return a list of modules to load global fixtures from"""
    return [
        transform_file_path_to_python_module_string(fixture)
        for fixture in pathlib.Path(__file__).parent.rglob("fixtures.py")
    ]


pytest_plugins = get_all_fixtures()


@pytest.fixture(name="postgresql", scope="session")
def fixture_postgresql_engine() -> t.Generator[engine.Engine, None, None]:
    with postgres.PostgresContainer(image="postgres:14.1") as _postgres:
        database_url = _postgres.get_connection_url()

        _engine = sqlalchemy.create_engine(
            database_url.replace("***", "test"),
            json_serializer=database.json_serializer,
        )

        with pytest.MonkeyPatch.context() as monkeypatch:
            monkeypatch.setattr(database, "engine", _engine)

        migration.migrate_db(_engine, str(_engine.url).replace("***", "test"))

        yield _engine


@pytest.fixture(name="db", autouse=True)
def fixture_db(
    postgresql: engine.Engine, monkeypatch: pytest.MonkeyPatch
) -> t.Generator[orm.Session, None, None]:
    session = orm.sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=postgresql,
    )()

    def mock_get_db() -> orm.Session:
        return session

    app.dependency_overrides[database.get_db] = mock_get_db

    def commit(*args, **kwargs):
        session.flush()
        session.expire_all()

    close = session.close

    monkeypatch.setattr(database, "SessionLocal", lambda: session)
    monkeypatch.setattr(session, "commit", commit)

    # Do not close the session; we'll reuse it for the test
    monkeypatch.setattr(session, "close", lambda *args, **kwargs: None)

    try:
        yield session
    finally:
        close()
        del app.dependency_overrides[database.get_db]


@pytest.fixture(name="private_rsa_key", scope="session")
def fixture_private_rsa_key() -> rsa.RSAPrivateKey:
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
    )


@pytest.fixture(name="id_token")
def fixture_id_token(
    executor_name: str, private_rsa_key: rsa.RSAPrivateKey
) -> str:
    return jwt.encode(
        {
            "sub": executor_name,
        },
        key=private_rsa_key,
        algorithm="RS256",
    )


@pytest.fixture(name="client")
def fixture_client(id_token: str) -> testclient.TestClient:
    return testclient.TestClient(
        app,
        cookies={"id_token": id_token},
    )


@pytest.fixture(name="client_pat")
def fixture_client_pat(
    user: users_models.DatabaseUser,
    pat_password: str,
) -> testclient.TestClient:
    encoded_credentials = base64.b64encode(
        f"{user.name}:{pat_password}".encode()
    ).decode()
    return testclient.TestClient(
        app, headers={"Authorization": f"Basic {encoded_credentials}"}
    )


@pytest.fixture(name="client_unauthenticated")
def fixture_client_unauthenticated() -> testclient.TestClient:
    return testclient.TestClient(app)


@pytest.fixture(name="logger")
def fixture_logger() -> logging.LoggerAdapter:
    return logging.LoggerAdapter(logging.getLogger())


@pytest.fixture(name="aiomock")
def fixture_aiomock() -> t.Generator[aioresponses.aioresponses, None, None]:
    with aioresponses.aioresponses() as _aioresponses:
        yield _aioresponses


@pytest.fixture(name="freeze_time")
def fixture_freeze_time(monkeypatch: pytest.MonkeyPatch) -> datetime.datetime:
    """
    Fixture to freeze the time for tests.
    Use this fixture to set a specific time for your tests.
    """

    time = datetime.datetime(2025, 2, 1, 9, 1, 27, 0, tzinfo=datetime.UTC)

    class MockDatetime(datetime.datetime):
        @classmethod
        def now(cls, tz=None):
            if tz is None:
                return time
            return time.astimezone(tz)

    monkeypatch.setattr(datetime, "datetime", MockDatetime)

    return time


@pytest.fixture(name="scheduler", autouse=True)
def fixture_scheduler(
    monkeypatch: pytest.MonkeyPatch,
) -> t.Generator[None, None, None]:
    """
    Fixture to mock the scheduler.
    Use this fixture to mock the scheduler for your tests.
    """

    scheduler = ap_background_scheduler.BackgroundScheduler(
        jobstores={"default": ap_memory.MemoryJobStore()},
        executors=scheduling.executors,
        timezone=datetime.UTC,
    )

    monkeypatch.setattr(scheduling, "scheduler", scheduler)
    scheduler.start(paused=True)

    yield

    scheduler.remove_all_jobs()
    scheduler.shutdown()
