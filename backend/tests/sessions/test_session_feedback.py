# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from unittest import mock

import pytest
from fastapi import testclient
from sqlalchemy import orm

import capellacollab.feedback.util
from capellacollab.config import models as config_models
from capellacollab.settings.configuration import crud as configuration_crud


@pytest.fixture(name="smtp_config_set")
def mock_smtp_config_set(monkeypatch: pytest.MonkeyPatch):
    mocked_config = config_models.AppConfig(
        smtp=config_models.SmtpConfig(
            enabled=True,
            host="smtp.example.com:587",
            user="smtp_user",
            password="smtp_password",
            sender="capella@example.com",
        )
    )
    monkeypatch.setattr(capellacollab.feedback.util, "config", mocked_config)


@pytest.fixture(name="smtp_config_not_set")
def mock_smtp_config_not_set(monkeypatch: pytest.MonkeyPatch):
    mocked_config = config_models.AppConfig(smtp=None)
    monkeypatch.setattr(capellacollab.feedback.util, "config", mocked_config)


@pytest.fixture(name="feedback_enabled")
def mock_feedback_enabled(db: orm.Session):
    configuration_crud.create_configuration(
        db, "global", {"feedback": {"enabled": True}}
    )


@pytest.fixture(name="feedback_disabled")
def mock_feedback_disabled(db: orm.Session):
    configuration_crud.create_configuration(
        db, "global", {"feedback": {"enabled": False}}
    )


@pytest.mark.usefixtures("user")
@pytest.mark.usefixtures("smtp_config_set")
@pytest.mark.usefixtures("feedback_enabled")
def test_send_feedback(
    client: testclient.TestClient,
):
    with mock.patch(
        "capellacollab.feedback.routes.send_email"
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

        assert response.status_code == 200
        assert response.json() == {"status": "sending"}

        send_email_mock.assert_called_once()


@pytest.mark.usefixtures("user")
@pytest.mark.usefixtures("smtp_config_set")
@pytest.mark.usefixtures("feedback_enabled")
def test_send_feedback_with_contact(
    client: testclient.TestClient,
):
    with mock.patch(
        "capellacollab.feedback.routes.send_email"
    ) as send_email_mock:
        response = client.post(
            "/api/v1/feedback",
            json={
                "rating": "good",
                "share_contact": True,
                "sessions": [],
                "feedback_text": None,
                "trigger": "test",
            },
        )

        assert response.status_code == 200
        assert response.json() == {"status": "sending"}

        send_email_mock.assert_called_once()


@pytest.mark.usefixtures("user")
@pytest.mark.usefixtures("smtp_config_set")
@pytest.mark.usefixtures("feedback_disabled")
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
    assert response.status_code == 500


@pytest.mark.usefixtures("user")
@pytest.mark.usefixtures("smtp_config_not_set")
@pytest.mark.usefixtures("feedback_enabled")
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
    assert response.status_code == 500


@pytest.mark.usefixtures("user")
@pytest.mark.usefixtures("smtp_config_not_set")
@pytest.mark.usefixtures("feedback_disabled")
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
    assert response.status_code == 500
