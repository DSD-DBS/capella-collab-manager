# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import testclient
from sqlalchemy import orm

from capellacollab.announcements import crud as announcements_crud
from capellacollab.announcements import models as announcements_models
from capellacollab.users import models as users_models


def test_get_announcements(
    client: testclient.TestClient,
    db: orm.Session,
):
    announcement = announcements_crud.create_announcement(
        db,
        announcements_models.CreateAnnouncementRequest(
            level=announcements_models.AnnouncementLevel.INFO,
            title="test title",
            message="test message",
            dismissible=True,
        ),
    )

    response = client.get("/api/v1/announcements")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert {
        "level": "info",
        "title": "test title",
        "message": "test message",
        "dismissible": True,
    }.items() <= response.json()[1].items()

    single_response = client.get(f"/api/v1/announcements/{announcement.id}")
    assert single_response.status_code == 200
    assert {
        "level": "info",
        "title": "test title",
        "message": "test message",
        "dismissible": True,
    }.items() <= single_response.json().items()


def test_get_missing_announcement(
    client: testclient.TestClient,
    db: orm.Session,
):
    response = client.get("/api/v1/announcements/99")

    assert response.status_code == 404
    assert response.json()["detail"]["err_code"] == "ANNOUNCEMENT_NOT_FOUND"


def test_create_announcement(
    client: testclient.TestClient,
    admin: users_models.DatabaseUser,
    db: orm.Session,
):
    response = client.post(
        "/api/v1/announcements",
        json={
            "title": "test",
            "message": "test",
            "level": "success",
            "dismissible": True,
        },
    )

    assert response.status_code == 200

    announcements = announcements_crud.get_announcements(db)

    assert len(announcements) == 2
    assert announcements[1].title == "test"
    assert announcements[1].message == "test"
    assert (
        announcements[1].level
        == announcements_models.AnnouncementLevel.SUCCESS
    )


def test_update_announcement(
    client: testclient.TestClient,
    admin: users_models.DatabaseUser,
    db: orm.Session,
):
    announcement = announcements_crud.create_announcement(
        db,
        announcements_models.CreateAnnouncementRequest(
            level=announcements_models.AnnouncementLevel.INFO,
            title="original title",
            message="original message",
            dismissible=True,
        ),
    )

    update_data = {
        "title": "updated title",
        "message": "updated message",
        "level": "warning",
        "dismissible": False,
    }

    response = client.patch(
        f"/api/v1/announcements/{announcement.id}", json=update_data
    )

    assert response.status_code == 200

    updated_announcement = announcements_crud.get_announcement_by_id(
        db, announcement.id
    )

    assert updated_announcement.title == "updated title"
    assert updated_announcement.message == "updated message"
    assert (
        updated_announcement.level
        == announcements_models.AnnouncementLevel.WARNING
    )
    assert updated_announcement.dismissible is False


def test_delete_announcement(
    client: testclient.TestClient,
    admin: users_models.DatabaseUser,
    db: orm.Session,
):
    announcement = announcements_crud.create_announcement(
        db,
        announcements_models.CreateAnnouncementRequest(
            level=announcements_models.AnnouncementLevel.INFO,
            title="test title",
            message="test message",
            dismissible=True,
        ),
    )

    response = client.delete(f"/api/v1/announcements/{announcement.id}")

    assert response.status_code == 204

    announcements = announcements_crud.get_announcements(db)
    assert len(announcements) == 1
