# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


from capellacollab.core import database  # isort: split

import logging
import os
import pathlib
import typing as t

import pytest
import sqlalchemy
import sqlalchemy.exc
from fastapi import testclient
from sqlalchemy import engine, orm
from testcontainers import postgres

from capellacollab.__main__ import app
from capellacollab.core.database import migration

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
def fixture_postgreql_engine() -> t.Generator[engine.Engine, None, None]:
    with postgres.PostgresContainer(image="postgres:14.1") as _postgres:
        database_url = _postgres.get_connection_url()

        with pytest.MonkeyPatch.context() as monkeypatch:
            _engine = sqlalchemy.create_engine(
                database_url.replace("***", "test")
            )

            session_local = orm.sessionmaker(
                autocommit=False, autoflush=False, bind=_engine
            )

            monkeypatch.setattr(database, "engine", _engine)
            monkeypatch.setattr(database, "SessionLocal", session_local)

            migration.migrate_db(
                _engine, str(_engine.url).replace("***", "test")
            )

            yield _engine


@pytest.fixture(name="db")
def fixture_db(
    postgresql: engine.Engine, monkeypatch: pytest.MonkeyPatch
) -> t.Generator[orm.Session, None, None]:
    with orm.sessionmaker(
        autocommit=False, autoflush=False, bind=postgresql
    )() as session:

        def mock_get_db() -> orm.Session:
            return session

        app.dependency_overrides[database.get_db] = mock_get_db

        # pylint: disable=unused-argument
        def commit(*args, **kwargs):
            session.flush()
            session.expire_all()

        monkeypatch.setattr(database, "SessionLocal", lambda: session)
        monkeypatch.setattr(session, "commit", commit)

        yield session

        del app.dependency_overrides[database.get_db]


@pytest.fixture(name="client")
def fixture_client() -> testclient.TestClient:
    return testclient.TestClient(app, cookies={"id_token": "any"})


@pytest.fixture(name="client_unauthenticated")
def fixture_client_unauthenticated() -> testclient.TestClient:
    return testclient.TestClient(app)


@pytest.fixture(name="logger")
def fixture_logger() -> logging.LoggerAdapter:
    return logging.LoggerAdapter(logging.getLogger())
