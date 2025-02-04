# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import base64
import logging
import os
import pathlib
import typing as t

import jwt
import pytest
import sqlalchemy
import sqlalchemy.exc
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import testclient
from sqlalchemy import engine, orm
from testcontainers import postgres

from capellacollab.__main__ import app
from capellacollab.core import database
from capellacollab.core.database import migration
from capellacollab.users import models as users_models
from capellacollab.users.tokens import models as tokens_models

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

    # pylint: disable=unused-argument
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
    pat: tuple[tokens_models.DatabaseUserToken, str],
) -> testclient.TestClient:
    encoded_credentials = base64.b64encode(
        f"{user.name}:{pat[1]}".encode()
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
