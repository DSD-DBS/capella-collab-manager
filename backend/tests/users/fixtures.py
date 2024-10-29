# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t
import uuid

import fastapi
import pytest
from sqlalchemy import orm

from capellacollab.__main__ import app
from capellacollab.core.authentication.api_key_cookie import JWTAPIKeyCookie
from capellacollab.users import crud as users_crud
from capellacollab.users import injectables as users_injectables
from capellacollab.users import models as users_models
from capellacollab.users.workspaces import crud as users_workspaces_crud
from capellacollab.users.workspaces import models as users_workspaces_models


@pytest.fixture(name="executor_name")
def fixture_executor_name(monkeypatch: pytest.MonkeyPatch) -> str:
    name = str(uuid.uuid1())

    # pylint: disable=unused-argument
    async def cookie_passthrough(self, request: fastapi.Request):
        return name

    monkeypatch.setattr(JWTAPIKeyCookie, "__init__", lambda self: None)
    monkeypatch.setattr(JWTAPIKeyCookie, "__call__", cookie_passthrough)

    return name


@pytest.fixture(name="unique_username")
def fixture_unique_username() -> str:
    return str(uuid.uuid1())


@pytest.fixture(name="basic_user")
def fixture_basic_user(
    db: orm.Session, executor_name: str
) -> users_models.DatabaseUser:
    return users_crud.create_user(
        db, executor_name, executor_name, None, users_models.Role.USER
    )


@pytest.fixture(name="user")
def fixture_user(
    basic_user: users_models.DatabaseUser,
) -> t.Generator[users_models.DatabaseUser, None, None]:
    def get_mock_own_user():
        return basic_user

    app.dependency_overrides[users_injectables.get_own_user] = (
        get_mock_own_user
    )
    yield basic_user
    del app.dependency_overrides[users_injectables.get_own_user]


@pytest.fixture(name="admin")
def fixture_admin(
    db: orm.Session, executor_name: str
) -> t.Generator[users_models.DatabaseUser, None, None]:
    admin = users_crud.create_user(
        db, executor_name, executor_name, None, users_models.Role.ADMIN
    )

    def get_mock_own_user():
        return admin

    app.dependency_overrides[users_injectables.get_own_user] = (
        get_mock_own_user
    )
    yield admin
    del app.dependency_overrides[users_injectables.get_own_user]


@pytest.fixture(name="test_user")
def fixture_test_user(db: orm.Session) -> users_models.DatabaseUser:
    return users_crud.create_user(
        db, "testuser", "testuser", None, users_models.Role.USER
    )


@pytest.fixture(name="user_workspace")
def fixture_user_workspace(
    db: orm.Session, test_user: users_models.DatabaseUser
) -> users_workspaces_models.DatabaseWorkspace:
    return users_workspaces_crud.create_workspace(
        db,
        users_workspaces_models.DatabaseWorkspace(
            "mock-workspace", "20Gi", test_user
        ),
    )
