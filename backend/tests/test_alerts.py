# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Sequence

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from capellacollab.notices.crud import (
    create_notice,
    delete_notice,
    get_notices,
)
from capellacollab.notices.models import (
    CreateNoticeRequest,
    DatabaseNotice,
    NoticeLevel,
)
from capellacollab.users.crud import create_user
from capellacollab.users.models import Role


@pytest.fixture(autouse=True)
def cleanup_notices(db: Session):
    for notice in get_notices(db):
        delete_notice(db, notice)


def test_get_alerts(client: TestClient, db: Session, executor_name: str):
    create_user(db, executor_name, Role.USER)
    create_notice(
        db,
        CreateNoticeRequest(
            level=NoticeLevel.INFO, title="test title", message="test message"
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


def test_create_alert_not_authenticated(client: TestClient):
    response = client.post(
        "/api/v1/notices",
        json={"title": "test", "message": "test", "level": "success"},
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_create_alert2(client: TestClient, db: Session, executor_name: str):
    create_user(db, executor_name, Role.ADMIN)

    response = client.post(
        "/api/v1/notices",
        json={"title": "test", "message": "test", "level": "success"},
    )

    assert response.status_code == 200

    notices: Sequence[DatabaseNotice] = get_notices(db)
    assert len(notices) == 1
    assert notices[0].title == "test"
    assert notices[0].message == "test"
    assert notices[0].level == NoticeLevel.SUCCESS


def test_delete_alert(client: TestClient, db: Session, executor_name: str):
    create_user(db, executor_name, Role.ADMIN)
    alert = create_notice(
        db,
        CreateNoticeRequest(
            level=NoticeLevel.INFO, title="test title", message="test message"
        ),
    )

    response = client.delete(f"/api/v1/notices/{alert.id}")

    assert response.status_code == 204
    assert not get_notices(db)
