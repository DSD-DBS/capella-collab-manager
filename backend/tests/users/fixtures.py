# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t
import uuid

import fastapi
import pytest
from sqlalchemy import orm

import capellacollab.users.models as users_models
from capellacollab.__main__ import app
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.users import crud as users_crud
from capellacollab.users import injectables as users_injectables
from capellacollab.users import models as users_models


@pytest.fixture(name="executor_name")
def fixture_executor_name(monkeypatch: pytest.MonkeyPatch) -> str:
    name = str(uuid.uuid1())

    # pylint: disable=unused-argument
    async def bearer_passthrough(self, request: fastapi.Request):
        return name

    monkeypatch.setattr(JWTBearer, "__call__", bearer_passthrough)

    return name


@pytest.fixture(name="unique_username")
def fixture_unique_username() -> str:
    return str(uuid.uuid1())


@pytest.fixture(name="basic_user")
def fixture_basic_user(
    db: orm.Session, executor_name: str
) -> users_models.DatabaseUser:
    return users_crud.create_user(db, executor_name, users_models.Role.USER)


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
    admin = users_crud.create_user(db, executor_name, users_models.Role.ADMIN)

    def get_mock_own_user():
        return admin

    app.dependency_overrides[users_injectables.get_own_user] = (
        get_mock_own_user
    )
    yield admin
    del app.dependency_overrides[users_injectables.get_own_user]
