# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t
import uuid

import fastapi
import pytest
from sqlalchemy import orm

from capellacollab.__main__ import app
from capellacollab.core.authentication import api_key_cookie
from capellacollab.permissions import models as permissions_models
from capellacollab.projects import models as projects_models
from capellacollab.projects.permissions import crud as project_permissions_crud
from capellacollab.projects.permissions import (
    models as projects_permissions_models,
)
from capellacollab.users import crud as users_crud
from capellacollab.users import injectables as users_injectables
from capellacollab.users import models as users_models
from capellacollab.users.tokens import crud as tokens_crud
from capellacollab.users.tokens import models as tokens_models
from capellacollab.users.workspaces import crud as users_workspaces_crud
from capellacollab.users.workspaces import models as users_workspaces_models


@pytest.fixture(name="executor_name")
def fixture_executor_name(monkeypatch: pytest.MonkeyPatch) -> str:
    name = str(uuid.uuid1())


    async def cookie_passthrough(self, request: fastapi.Request):
        return name

    monkeypatch.setattr(
        api_key_cookie.JWTAPIKeyCookie, "__init__", lambda self: None
    )
    monkeypatch.setattr(
        api_key_cookie.JWTAPIKeyCookie, "__call__", cookie_passthrough
    )

    return name


@pytest.fixture(name="basic_user")
def fixture_basic_user(
    db: orm.Session, executor_name: str
) -> users_models.DatabaseUser:
    return users_crud.create_user(
        db, executor_name, executor_name, None, users_models.Role.USER
    )


@pytest.fixture(name="user2")
def fixture_user2(db: orm.Session) -> users_models.DatabaseUser:
    return users_crud.create_user(
        db, "user2", "user2", None, users_models.Role.USER
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
    user: users_models.DatabaseUser,
) -> users_models.DatabaseUser:
    user.role = users_models.Role.ADMIN
    return user


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


@pytest.fixture(
    name="pat_scope",
    params=[
        (
            permissions_models.GlobalScopes(),
            projects_permissions_models.ProjectUserScopes(),
        )
    ],
)
def fixture_pat_scope(
    request: pytest.FixtureRequest,
) -> tuple[
    permissions_models.GlobalScopes | None,
    projects_permissions_models.ProjectUserScopes | None,
]:
    return request.param


@pytest.fixture(name="pat")
def fixture_pat(
    db: orm.Session,
    user: users_models.DatabaseUser,
    pat_scope: tuple[
        permissions_models.GlobalScopes | None,
        projects_permissions_models.ProjectUserScopes,
    ],
    project: projects_models.DatabaseProject,
) -> tuple[tokens_models.DatabaseUserToken, str]:
    global_scope, project_scope = pat_scope
    if global_scope is None:
        global_scope = permissions_models.GlobalScopes()

    token, password = tokens_crud.create_token(
        db,
        user,
        scope=global_scope,
        title="test",
        description="",
        expiration_date=None,
        source="test",
    )

    if project_scope:
        project_permissions_crud.create_personal_access_token_link(
            db, project, token, project_scope
        )

    return token, password
