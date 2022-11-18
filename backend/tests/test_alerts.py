# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from capellacollab.notices.crud import (
    create_notice,
    delete_notice,
    get_all_notices,
)
from capellacollab.notices.models import (
    CreateNoticeRequest,
    DatabaseNotice,
    NoticeLevel,
)
from capellacollab.users.crud import create_user
from capellacollab.users.models import Role


def test_get_alerts(client: TestClient, db: Session, username: str):
    create_user(db, username, Role.USER)
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

    delete_notice(db, get_all_notices(db)[0])


def test_create_alert_not_authenticated(client: TestClient):
    response = client.post(
        "/api/v1/notices",
        {"title": "test", "message": "test", "level": "success"},
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_create_alert(client: TestClient, db: Session, username: str):
    create_user(db, username, Role.ADMIN)

    response = client.post(
        "/api/v1/notices",
        json={"title": "test", "message": "test", "level": "success"},
    )

    assert response.status_code == 200

    notices: list[DatabaseNotice] = get_all_notices(db)
    assert len(notices) == 1
    assert notices[0].title == "test"
    assert notices[0].message == "test"
    assert notices[0].level == NoticeLevel.SUCCESS

    delete_notice(db, notices[0])


def test_delete_alert(client: TestClient, db: Session, username: str):
    create_user(db, username, Role.ADMIN)
    alert = create_notice(
        db,
        CreateNoticeRequest(
            level=NoticeLevel.INFO, title="test title", message="test message"
        ),
    )

    response = client.delete(f"/api/v1/notices/{alert.id}")

    assert response.status_code == 204
    assert len(get_all_notices(db)) == 0
