# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from collections import abc

from fastapi.testclient import TestClient
from sqlalchemy import orm

from capellacollab.notices import crud as notices_crud
from capellacollab.notices import models as notices_models
from capellacollab.users import crud as users_crud
from capellacollab.users import models as users_models


def test_get_alerts(client: TestClient, db: orm.Session, executor_name: str):
    users_crud.create_user(
        db, executor_name, executor_name, None, users_models.Role.USER
    )
    notice = notices_crud.create_notice(
        db,
        notices_models.CreateNoticeRequest(
            level=notices_models.NoticeLevel.INFO,
            title="test title",
            message="test message",
        ),
    )

    response = client.get("/api/v1/notices")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert {
        "level": "info",
        "title": "test title",
        "message": "test message",
    }.items() <= response.json()[0].items()

    single_response = client.get(f"/api/v1/notices/{notice.id}")
    assert single_response.status_code == 200
    assert {
        "level": "info",
        "title": "test title",
        "message": "test message",
    }.items() <= single_response.json().items()


def test_get_missing_alert(
    client: TestClient, db: orm.Session, executor_name: str
):
    response = client.get("/api/v1/notices/1")

    assert response.status_code == 404
    assert response.json()["detail"]["err_code"] == "ANNOUNCEMENT_NOT_FOUND"


def test_create_alert2(
    client: TestClient, db: orm.Session, executor_name: str
):
    users_crud.create_user(
        db, executor_name, executor_name, None, users_models.Role.ADMIN
    )

    response = client.post(
        "/api/v1/notices",
        json={"title": "test", "message": "test", "level": "success"},
    )

    assert response.status_code == 200

    notices: abc.Sequence[notices_models.DatabaseNotice] = (
        notices_crud.get_notices(db)
    )
    assert len(notices) == 1
    assert notices[0].title == "test"
    assert notices[0].message == "test"
    assert notices[0].level == notices_models.NoticeLevel.SUCCESS


def test_delete_alert(client: TestClient, db: orm.Session, executor_name: str):
    users_crud.create_user(
        db, executor_name, executor_name, None, users_models.Role.ADMIN
    )
    alert = notices_crud.create_notice(
        db,
        notices_models.CreateNoticeRequest(
            level=notices_models.NoticeLevel.INFO,
            title="test title",
            message="test message",
        ),
    )

    response = client.delete(f"/api/v1/notices/{alert.id}")

    assert response.status_code == 204
    assert not notices_crud.get_notices(db)
