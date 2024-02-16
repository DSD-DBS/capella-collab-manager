# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import os
from uuid import uuid1

import fastapi
import pytest
import sqlalchemy
import sqlalchemy.exc
from fastapi import testclient
from sqlalchemy import engine, orm
from testcontainers import postgres

from capellacollab.core import database  # isort: split

import typing as t

import capellacollab.projects.crud as projects_crud
import capellacollab.projects.models as projects_models
import capellacollab.projects.users.crud as projects_users_crud
import capellacollab.projects.users.models as projects_users_models
import capellacollab.users.models as users_models
from capellacollab.__main__ import app
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.database import migration
from capellacollab.users import crud as users_crud
from capellacollab.users import injectables as users_injectables

os.environ["DEVELOPMENT_MODE"] = "1"


@pytest.fixture(name="postgresql", scope="session")
def fixture_postgresql() -> t.Generator[engine.Engine, None, None]:
    with postgres.PostgresContainer(image="postgres:14.1") as _postgres:
        database_url = _postgres.get_connection_url()

        _engine = sqlalchemy.create_engine(database_url.replace("***", "test"))

        yield _engine


@pytest.fixture(name="db")
def fixture_db(
    postgresql: engine.Engine, monkeypatch: pytest.MonkeyPatch
) -> t.Generator[orm.Session, None, None]:
    session_local = orm.sessionmaker(
        autocommit=False, autoflush=False, bind=postgresql
    )

    monkeypatch.setattr(database, "engine", postgresql)
    monkeypatch.setattr(database, "SessionLocal", session_local)

    delete_all_tables_if_existent(postgresql)
    migration.migrate_db(
        postgresql, str(postgresql.url).replace("***", "test")
    )

    with session_local() as session:

        def mock_get_db() -> orm.Session:
            return session

        app.dependency_overrides[database.get_db] = mock_get_db

        yield session


@pytest.fixture(name="executor_name")
def fixture_executor_name(monkeypatch: pytest.MonkeyPatch) -> str:
    name = str(uuid1())

    # pylint: disable=unused-argument
    async def bearer_passthrough(self, request: fastapi.Request):
        return name

    monkeypatch.setattr(JWTBearer, "__call__", bearer_passthrough)

    return name


@pytest.fixture(name="unique_username")
def fixture_unique_username() -> str:
    return str(uuid1())


@pytest.fixture(name="admin")
def fixture_admin(
    db: orm.Session, executor_name: str
) -> t.Generator[users_models.DatabaseUser, None, None]:
    admin = users_crud.create_user(db, executor_name, users_models.Role.ADMIN)

    def get_mock_own_user():
        return admin

    app.dependency_overrides[users_injectables.get_own_user] = (
        get_mock_own_user
    )
    yield admin
    del app.dependency_overrides[users_injectables.get_own_user]


@pytest.fixture(name="user")
def fixture_user(
    db: orm.Session, executor_name: str
) -> t.Generator[users_models.DatabaseUser, None, None]:
    user = users_crud.create_user(db, executor_name, users_models.Role.USER)

    def get_mock_own_user():
        return user

    app.dependency_overrides[users_injectables.get_own_user] = (
        get_mock_own_user
    )
    yield user
    del app.dependency_overrides[users_injectables.get_own_user]


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
    projects_users_crud.add_user_to_project(
        db,
        project=project,
        user=user,
        role=projects_users_models.ProjectUserRole.MANAGER,
        permission=projects_users_models.ProjectUserPermission.WRITE,
    )
    return user


@pytest.fixture
def project_user(
    db: orm.Session,
    project: projects_models.DatabaseProject,
    executor_name: str,
) -> users_models.DatabaseUser:
    user = users_crud.create_user(db, executor_name)
    projects_users_crud.add_user_to_project(
        db,
        project=project,
        user=user,
        role=projects_users_models.ProjectUserRole.USER,
        permission=projects_users_models.ProjectUserPermission.WRITE,
    )
    return user


@pytest.fixture()
def client() -> testclient.TestClient:
    return testclient.TestClient(app, headers={"Authorization": "bearer"})


def delete_all_tables_if_existent(_engine: sqlalchemy.engine.Engine) -> bool:
    """Delete complete database structure (including the alembic table)
    If one of the tables does not exist, this function doesn't raise an exception.

    Parameters
    ----------
    engine
        SQLAlchemy database engine

    Returns
    -------
    bool
        True if successful,
        False if sqlalchemy.exc.ProgrammingError occured during deletion,
        e.g., when the tables didn't exist.

    """
    try:
        database.Base.metadata.drop_all(_engine)
        t_alembic = sqlalchemy.Table(
            "alembic_version", sqlalchemy.MetaData(), autoload_with=_engine
        )
    except (sqlalchemy.exc.ProgrammingError, sqlalchemy.exc.NoSuchTableError):
        return False

    with _engine.connect() as session:
        session.execute(sqlalchemy.delete(t_alembic))
        session.commit()

    return True
