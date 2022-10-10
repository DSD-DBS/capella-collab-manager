# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from uuid import uuid1

import pytest
from fastapi import Request
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer

import capellacollab.core.database as database_
from capellacollab.__main__ import app
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.database import migration


@pytest.fixture(scope="session")
def postgresql():
    with PostgresContainer("postgres:14.1") as postgres:
        database_url = postgres.get_connection_url()
        engine = create_engine(database_url)

        yield engine


@pytest.fixture
def db(postgresql, monkeypatch):
    session_local = sessionmaker(
        autocommit=False, autoflush=False, bind=postgresql
    )

    monkeypatch.setattr(database_, "engine", postgresql)
    monkeypatch.setattr(database_, "SessionLocal", session_local)

    migration.migrate_db(postgresql)

    with session_local() as session:
        yield session


@pytest.fixture
def username(monkeypatch):
    name = str(uuid1())

    async def bearer_passthrough(self, request: Request):
        return {"sub": name}

    monkeypatch.setattr(JWTBearer, "__call__", bearer_passthrough)

    return name


@pytest.fixture
def client():
    return TestClient(app)
