# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from capellacollab.config import config

# Patch k8s values in order to load the kubectl configuration properly
if config["k8s"].get("context", None):
    del config["k8s"]["context"]
config["k8s"]["apiURL"] = "dummy"
config["k8s"]["token"] = "dummy"

from uuid import uuid1

import fastapi
import pytest
import sqlalchemy
from fastapi import testclient
from sqlalchemy import engine, orm
from testcontainers import postgres

import capellacollab.core.database as database
import capellacollab.projects.crud as projects_crud
import capellacollab.projects.models as projects_models
import capellacollab.projects.users.crud as project_users_crud
import capellacollab.projects.users.models as project_users_models
import capellacollab.users.crud as users_crud
import capellacollab.users.models as users_models
from capellacollab.__main__ import app
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.database import migration


@pytest.fixture(name="postgresql", scope="session")
def fixture_postgresql() -> engine.Engine:
    with postgres.PostgresContainer("postgres:14.1") as _postgres:
        database_url = _postgres.get_connection_url()
        _engine = sqlalchemy.create_engine(database_url)

        yield _engine


@pytest.fixture(name="db")
def fixture_db(
    postgresql: engine.Engine, monkeypatch: pytest.MonkeyPatch
) -> orm.Session:
    session_local = orm.sessionmaker(
        autocommit=False, autoflush=False, bind=postgresql
    )

    monkeypatch.setattr(database, "engine", postgresql)
    monkeypatch.setattr(database, "SessionLocal", session_local)

    migration.migrate_db(postgresql, str(postgresql.url))

    with session_local() as session:
        yield session


@pytest.fixture(name="executor_name")
def fixture_executor_name(monkeypatch: pytest.MonkeyPatch) -> str:
    name = str(uuid1())

    async def bearer_passthrough(self, request: fastapi.Request):
        return {"sub": name}

    monkeypatch.setattr(JWTBearer, "__call__", bearer_passthrough)

    return name


@pytest.fixture(name="unique_username")
def fixture_unique_username() -> str:
    return str(uuid1())


@pytest.fixture(name="project")
def fixture_project(db: orm.Session) -> projects_models.DatabaseProject:
    return projects_crud.create_project(db, str(uuid1()))


@pytest.fixture
def project_manager(
    db: orm.Session,
    project: projects_models.DatabaseProject,
    executor_name: str,
) -> users_models.DatabaseUser:
    user = users_crud.create_user(db, executor_name)
    project_users_crud.add_user_to_project(
        db,
        project=project,
        user=user,
        role=project_users_models.ProjectUserRole.MANAGER,
        permission=project_users_models.ProjectUserPermission.WRITE,
    )
    return user


@pytest.fixture
def client() -> testclient.TestClient:
    return testclient.TestClient(app)
