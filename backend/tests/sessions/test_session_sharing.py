# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime

import pytest
from fastapi import testclient
from sqlalchemy import orm

from capellacollab.__main__ import app
from capellacollab.sessions import crud as sessions_crud
from capellacollab.sessions import models as sessions_models
from capellacollab.tools import models as tools_models
from capellacollab.users import crud as users_crud
from capellacollab.users import injectables as users_injectables
from capellacollab.users import models as users_models


@pytest.fixture(name="enable_tool_session_sharing")
def fixture_enable_tool_session_sharing(
    tool: tools_models.DatabaseTool, db: orm.Session
):
    tool.config.connection.methods[0].sharing.enabled = True
    orm.attributes.flag_modified(tool, "config")
    db.commit()


@pytest.fixture(name="shared_with_user")
def fixture_shared_with_user(db: orm.Session) -> users_models.DatabaseUser:
    user2 = users_crud.create_user(
        db, "shared_with_user", users_models.Role.USER
    )
    return user2


@pytest.fixture(name="act_as_shared_with_user")
def fixture_act_as_shared_with_user(
    shared_with_user: users_models.DatabaseUser,
):
    def get_mock_own_user():
        return shared_with_user

    app.dependency_overrides[users_injectables.get_own_user] = (
        get_mock_own_user
    )
    yield shared_with_user
    del app.dependency_overrides[users_injectables.get_own_user]


@pytest.fixture(name="shared_session")
def fixture_shared_session(
    session: sessions_models.DatabaseSession,
    db: orm.Session,
    shared_with_user: users_models.DatabaseUser,
) -> sessions_models.DatabaseSession:
    sessions_crud.create_shared_session(
        db,
        sessions_models.DatabaseSharedSession(
            created_at=datetime.datetime.now(),
            session=session,
            user=shared_with_user,
        ),
    )
    return session


def test_share_session_with_owner_fails(
    session: sessions_models.DatabaseSession,
    user: users_models.DatabaseUser,
    client: testclient.TestClient,
):
    response = client.post(
        f"/api/v1/sessions/{session.id}/shares",
        json={
            "username": user.name,
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"]["err_code"] == "SESSION_ALREADY_SHARED"


@pytest.mark.usefixtures("enable_tool_session_sharing")
def test_session_is_already_shared(
    session: sessions_models.DatabaseSession,
    client: testclient.TestClient,
    db: orm.Session,
):
    user2 = users_crud.create_user(db, "user2", users_models.Role.USER)
    response = client.post(
        f"/api/v1/sessions/{session.id}/shares",
        json={
            "username": user2.name,
        },
    )

    assert response.status_code == 200

    # Try to share the session a second time
    response = client.post(
        f"/api/v1/sessions/{session.id}/shares",
        json={
            "username": user2.name,
        },
    )
    assert response.status_code == 409
    assert response.json()["detail"]["err_code"] == "SESSION_ALREADY_SHARED"


def test_user_to_share_with_doesnt_exist(
    session: sessions_models.DatabaseSession,
    client: testclient.TestClient,
):
    response = client.post(
        f"/api/v1/sessions/{session.id}/shares",
        json={
            "username": "invalid-user",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"]["err_code"] == "USER_NOT_FOUND"


@pytest.mark.usefixtures(
    "act_as_shared_with_user", "enable_tool_session_sharing"
)
def test_share_session_not_owned(
    db: orm.Session,
    shared_session: sessions_models.DatabaseSession,
    client: testclient.TestClient,
):
    user3 = users_crud.create_user(db, "user3", users_models.Role.USER)

    response = client.post(
        f"/api/v1/sessions/{shared_session.id}/shares",
        json={
            "username": user3.name,
        },
    )
    assert response.status_code == 403
    assert response.json()["detail"]["err_code"] == "SESSION_NOT_OWNED"


@pytest.mark.usefixtures("act_as_shared_with_user")
def test_terminate_session_not_owned(
    shared_session: sessions_models.DatabaseSession,
    client: testclient.TestClient,
):
    response = client.delete(
        f"/api/v1/sessions/{shared_session.id}",
    )

    assert response.status_code == 403
    assert response.json()["detail"]["err_code"] == "SESSION_NOT_OWNED"


@pytest.mark.usefixtures("enable_tool_session_sharing")
def test_share_session(
    session: sessions_models.DatabaseSession,
    client: testclient.TestClient,
    db: orm.Session,
):
    user2 = users_crud.create_user(db, "user2", users_models.Role.USER)
    response = client.post(
        f"/api/v1/sessions/{session.id}/shares",
        json={
            "username": user2.name,
        },
    )

    assert response.status_code == 200

    response = client.get(f"/api/v1/sessions/{session.id}")

    assert response.status_code == 200
    assert len(response.json()["shared_with"]) == 1
    assert response.json()["shared_with"][0]["user"]["name"] == user2.name


@pytest.mark.usefixtures("act_as_shared_with_user")
def test_connect_to_shared_session(
    shared_session: sessions_models.DatabaseSession,
    client: testclient.TestClient,
):
    response = client.get(
        f"/api/v1/sessions/{shared_session.id}/connection",
    )

    assert response.status_code == 200


@pytest.mark.usefixtures(
    "act_as_shared_with_user", "enable_tool_session_sharing"
)
def test_connect_to_unshared_session_fails(
    session: sessions_models.DatabaseSession,
    client: testclient.TestClient,
):
    response = client.get(
        f"/api/v1/sessions/{session.id}/connection",
    )

    assert response.status_code == 403
    assert response.json()["detail"]["err_code"] == "SESSION_NOT_OWNED"


@pytest.mark.usefixtures("act_as_shared_with_user")
def test_shared_session_in_user_sessions(
    shared_session: sessions_models.DatabaseSession,
    client: testclient.TestClient,
    shared_with_user: users_models.DatabaseUser,
    basic_user: users_models.DatabaseUser,
):
    response = client.get(f"/api/v1/users/{shared_with_user.id}/sessions")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == shared_session.id
    assert response.json()[0]["owner"]["id"] == basic_user.id


def test_tool_doesnt_support_sharing(
    session: sessions_models.DatabaseSession,
    db: orm.Session,
    client: testclient.TestClient,
):
    user2 = users_crud.create_user(db, "user2", users_models.Role.USER)
    response = client.post(
        f"/api/v1/sessions/{session.id}/shares",
        json={
            "username": user2.name,
        },
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]["err_code"] == "SESSION_SHARING_UNSUPPORTED"
    )
