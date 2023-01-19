# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from uuid import uuid1

import pytest
from fastapi import Request
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from testcontainers.postgres import PostgresContainer

from capellacollab.config import config

# Patch k8s values in order to load the kubectl configuration properly
if config["k8s"].get("context", None):
    del config["k8s"]["context"]
config["k8s"]["apiURL"] = "dummy"
config["k8s"]["token"] = "dummy"

import capellacollab.core.database as database_
from capellacollab.__main__ import app
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.database import migration
from capellacollab.projects.crud import create_project


@pytest.fixture(scope="session")
def postgresql():
    with PostgresContainer("postgres:14.1") as postgres:
        database_url = postgres.get_connection_url()
        engine = create_engine(database_url)

        yield engine


@pytest.fixture
def db(postgresql, monkeypatch) -> Session:
    session_local = sessionmaker(
        autocommit=False, autoflush=False, bind=postgresql
    )

    monkeypatch.setattr(database_, "engine", postgresql)
    monkeypatch.setattr(database_, "SessionLocal", session_local)

    migration.migrate_db(postgresql, str(postgresql.url))

    with session_local() as session:
        yield session


@pytest.fixture
def executor_name(monkeypatch):
    name = str(uuid1())

    async def bearer_passthrough(self, request: Request):
        return {"sub": name}

    monkeypatch.setattr(JWTBearer, "__call__", bearer_passthrough)

    return name


@pytest.fixture
def unique_username():
    return str(uuid1())


@pytest.fixture
def project(db):
    return create_project(db, str(uuid1()))


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
