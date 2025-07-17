# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
from unittest import mock

import pytest

from capellacollab.core.email import send as email_send
from capellacollab.sessions import alerting as sessions_alerting
from capellacollab.sessions import models as sessions_models
from capellacollab.sessions.operators import k8s


def test_pending_session_two_minutes(
    monkeypatch: pytest.MonkeyPatch,
    session: sessions_models.DatabaseSession,
):
    """Test that a session doesn't raise an alert if pending for two minutes."""
    monkeypatch.setattr(
        k8s.KubernetesOperator,
        "get_session_state",
        lambda self, session_id: (
            sessions_models.SessionPreparationState.COMPLETED,
            sessions_models.SessionState.PENDING,
        ),
    )
    session.created_at = datetime.datetime.now(
        tz=datetime.UTC
    ) - datetime.timedelta(minutes=2)

    mock_send_email = mock.Mock()

    monkeypatch.setattr(
        email_send,
        "send_email",
        mock_send_email,
    )

    sessions_alerting.alert_on_failed_or_pending_sessions()

    assert mock_send_email.call_count == 0


def test_pending_session_ten_minutes(
    monkeypatch: pytest.MonkeyPatch,
    session: sessions_models.DatabaseSession,
):
    """Test that a session raises an alert if pending for seven minutes."""
    monkeypatch.setattr(
        k8s.KubernetesOperator,
        "get_session_state",
        lambda self, session_id: (
            sessions_models.SessionPreparationState.COMPLETED,
            sessions_models.SessionState.PENDING,
        ),
    )
    session.created_at = datetime.datetime.now(
        tz=datetime.UTC
    ) - datetime.timedelta(minutes=10)

    mock_send_email = mock.Mock()

    monkeypatch.setattr(
        email_send,
        "send_email",
        mock_send_email,
    )

    sessions_alerting.alert_on_failed_or_pending_sessions()

    assert mock_send_email.call_count == 1


def test_successful_session_no_alert(
    monkeypatch: pytest.MonkeyPatch,
    session: sessions_models.DatabaseSession,
):
    """Test that a successful session doesn't raise an alert"""
    monkeypatch.setattr(
        k8s.KubernetesOperator,
        "get_session_state",
        lambda self, session_id: (
            sessions_models.SessionPreparationState.COMPLETED,
            sessions_models.SessionState.RUNNING,
        ),
    )
    session.created_at = datetime.datetime.now(
        tz=datetime.UTC
    ) - datetime.timedelta(minutes=10)

    mock_send_email = mock.Mock()

    monkeypatch.setattr(
        email_send,
        "send_email",
        mock_send_email,
    )

    sessions_alerting.alert_on_failed_or_pending_sessions()

    assert mock_send_email.call_count == 0


@pytest.mark.usefixtures("session")
def test_failed_session_preparation_alert(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that a failed session preparation leads to an alert"""
    monkeypatch.setattr(
        k8s.KubernetesOperator,
        "get_session_state",
        lambda self, session_id: (
            sessions_models.SessionPreparationState.FAILED,
            sessions_models.SessionState.PENDING,
        ),
    )

    mock_send_email = mock.Mock()

    monkeypatch.setattr(
        email_send,
        "send_email",
        mock_send_email,
    )

    sessions_alerting.alert_on_failed_or_pending_sessions()

    assert mock_send_email.call_count == 1


def test_failed_session_already_alerted(
    monkeypatch: pytest.MonkeyPatch,
    session: sessions_models.DatabaseSession,
):
    """Test that a failed session doesn't lead to a second alert"""

    session.alerted = True
    monkeypatch.setattr(
        k8s.KubernetesOperator,
        "get_session_state",
        lambda self, session_id: (
            sessions_models.SessionPreparationState.COMPLETED,
            sessions_models.SessionState.FAILED,
        ),
    )

    mock_send_email = mock.Mock()

    monkeypatch.setattr(
        email_send,
        "send_email",
        mock_send_email,
    )

    sessions_alerting.alert_on_failed_or_pending_sessions()

    assert mock_send_email.call_count == 0
