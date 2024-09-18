# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from unittest import mock

import pytest
from fastapi import testclient
from sqlalchemy import orm

from capellacollab.config import config
from capellacollab.config import models as config_models
from capellacollab.settings.configuration import crud as configuration_crud


@pytest.fixture(name="smtp_config_set")
def fixture_smtp_config_set(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        config,
        "smtp",
        config_models.SMTPConfig(
            enabled=True,
            host="smtp.example.com:587",
            user="smtp_user",
            password="smtp_password",
            sender="capella@example.com",
        ),
    )


@pytest.fixture(name="smtp_config_not_set")
def fixture_smtp_config_not_set(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(config, "smtp", None)


@pytest.fixture(name="feedback_enabled")
def fixture_feedback_enabled(db: orm.Session):
    configuration_crud.create_configuration(
        db, "global", {"feedback": {"enabled": True}}
    )


@pytest.fixture(name="feedback_disabled")
def fixture_feedback_disabled(db: orm.Session):
    configuration_crud.create_configuration(
        db, "global", {"feedback": {"enabled": False}}
    )


@pytest.mark.usefixtures("user", "smtp_config_set", "feedback_enabled")
def test_send_feedback(
    client: testclient.TestClient,
):
    with mock.patch(
        "capellacollab.core.email.send.send_email"
    ) as send_email_mock:
        response = client.post(
            "/api/v1/feedback",
            json={
                "rating": "good",
                "share_contact": False,
                "sessions": [],
                "feedback_text": None,
                "trigger": "test",
            },
        )

        assert response.status_code == 204
        send_email_mock.assert_called_once()


@pytest.mark.usefixtures("user", "smtp_config_set", "feedback_enabled")
def test_send_feedback_with_session(
    client: testclient.TestClient,
):
    with mock.patch(
        "capellacollab.core.email.send.send_email"
    ) as send_email_mock:
        response = client.post(
            "/api/v1/feedback",
            json={
                "rating": "good",
                "share_contact": False,
                "sessions": [
                    {
                        "id": "gqakbljquqenfmzvflacgqntx",
                        "type": "persistent",
                        "created_at": "2024-09-19T21:02:12Z",
                        "version": {
                            "id": 4,
                            "name": "6.1.0",
                            "tool": {"id": 1, "name": "Capella"},
                        },
                        "state": "Started",
                        "warnings": [],
                        "connection_method": {
                            "id": "xpra",
                            "name": "Experimental (Xpra)",
                        },
                    }
                ],
                "feedback_text": None,
                "trigger": "test",
            },
        )

        assert response.status_code == 204
        send_email_mock.assert_called_once()


@pytest.mark.usefixtures("user", "smtp_config_set", "feedback_enabled")
def test_send_feedback_with_contact(
    client: testclient.TestClient,
):
    with mock.patch(
        "capellacollab.core.email.send.send_email"
    ) as send_email_mock:
        response = client.post(
            "/api/v1/feedback",
            json={
                "rating": "good",
                "share_contact": True,
                "sessions": [],
                "feedback_text": None,
                "trigger": None,
            },
        )

        assert response.status_code == 204
        send_email_mock.assert_called_once()


@pytest.mark.usefixtures("user", "smtp_config_set", "feedback_disabled")
def test_send_feedback_fail_disabled(
    client: testclient.TestClient,
):
    response = client.post(
        "/api/v1/feedback",
        json={
            "rating": "good",
            "share_contact": False,
            "sessions": [],
            "feedback_text": None,
            "trigger": "test",
        },
    )
    assert response.status_code == 403
    assert response.json()["detail"]["err_code"] == "FEEDBACK_NOT_ENABLED"


@pytest.mark.usefixtures("user", "smtp_config_not_set", "feedback_enabled")
def test_send_feedback_fail_missing_smtp(
    client: testclient.TestClient,
):
    response = client.post(
        "/api/v1/feedback",
        json={
            "rating": "good",
            "share_contact": False,
            "sessions": [],
            "feedback_text": None,
            "trigger": "test",
        },
    )
    assert response.status_code == 403
    assert response.json()["detail"]["err_code"] == "SMTP_NOT_CONFIGURED"


@pytest.mark.usefixtures("user", "smtp_config_not_set", "feedback_disabled")
def test_send_feedback_fail_disabled_and_missing_smtp(
    client: testclient.TestClient,
):
    response = client.post(
        "/api/v1/feedback",
        json={
            "rating": "good",
            "share_contact": False,
            "sessions": [],
            "feedback_text": None,
            "trigger": "test",
        },
    )
    assert response.status_code == 403
    assert response.json()["detail"]["err_code"] == "SMTP_NOT_CONFIGURED"


@pytest.mark.usefixtures("admin")
def test_feedback_is_updated(
    client: testclient.TestClient,
):
    response = client.put(
        "/api/v1/settings/configurations/global",
        json={
            "feedback": {
                "enabled": True,
                "after_session": True,
                "on_footer": True,
                "on_session_card": True,
                "interval": {"enabled": True, "hours_between_prompt": 24},
                "recipients": ["test@example.com"],
            }
        },
    )

    assert response.status_code == 200

    response = client.get("/api/v1/configurations/feedback")
    assert response.status_code == 200
    assert response.json() == {
        "enabled": True,
        "after_session": True,
        "on_footer": True,
        "on_session_card": True,
        "interval": {"enabled": True, "hours_between_prompt": 24},
        "recipients": ["test@example.com"],
    }


@pytest.mark.usefixtures("admin", "smtp_config_not_set")
def test_activate_feedback_without_smtp(
    client: testclient.TestClient,
):
    response = client.put(
        "/api/v1/settings/configurations/global",
        json={
            "feedback": {
                "enabled": True,
            }
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"]["err_code"] == "SMTP_NOT_CONFIGURED"


@pytest.mark.usefixtures("admin", "smtp_config_set")
def test_activate_feedback_without_recipients(
    client: testclient.TestClient,
):
    response = client.put(
        "/api/v1/settings/configurations/global",
        json={
            "feedback": {
                "enabled": True,
                "recipients": [],
            }
        },
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]["err_code"] == "FEEDBACK_MISSING_RECIPIENTS"
    )


@pytest.mark.usefixtures("user", "smtp_config_not_set", "feedback_enabled")
def test_feedback_is_disabled_without_smtp(client: testclient.TestClient):
    response = client.get("/api/v1/configurations/feedback")
    assert response.status_code == 200
    assert response.json()["enabled"] is False
