# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging
from unittest import mock

import pydantic
import pytest
from sqlalchemy import orm

from capellacollab.configuration.app import config
from capellacollab.core.email import exceptions as email_exceptions
from capellacollab.core.email import models as email_models
from capellacollab.core.email import send as email_send
from capellacollab.projects.toolmodels.backups.runs import (
    alerting as pipeline_runs_alerting,
)
from capellacollab.projects.toolmodels.backups.runs import (
    models as pipeline_runs_models,
)


def test_pipeline_alerting_missing_configuration(
    monkeypatch: pytest.MonkeyPatch,
    db: orm.Session,
    pipeline_run: pipeline_runs_models.DatabasePipelineRun,
):
    """Test pipeline alerting with missing SMTP configuration."""
    pipeline_run.status = pipeline_runs_models.PipelineRunStatus.FAILURE

    def mock_send_email(
        recipients: list[pydantic.EmailStr],
        email: email_models.EMailContent,
        logger: logging.LoggerAdapter | None = None,
    ):
        raise email_exceptions.SMTPNotConfiguredError()

    monkeypatch.setattr(
        email_send,
        "send_email",
        mock_send_email,
    )

    pipeline_runs_alerting.send_alert_on_failed_pipeline_run(db, pipeline_run)


def test_pipeline_alerting_no_email_on_failure(
    monkeypatch: pytest.MonkeyPatch,
    db: orm.Session,
    pipeline_run: pipeline_runs_models.DatabasePipelineRun,
):
    """Test pipeline alerting when status is failure."""
    pipeline_run.status = pipeline_runs_models.PipelineRunStatus.FAILURE

    mock_send_email = mock.Mock()

    monkeypatch.setattr(
        email_send,
        "send_email",
        mock_send_email,
    )

    pipeline_runs_alerting.send_alert_on_failed_pipeline_run(db, pipeline_run)
    assert mock_send_email.call_count == 1


def test_pipeline_alerting_no_email_on_success(
    monkeypatch: pytest.MonkeyPatch,
    db: orm.Session,
    pipeline_run: pipeline_runs_models.DatabasePipelineRun,
):
    monkeypatch.setattr(config.smtp, "enabled", False)
    pipeline_run.status = pipeline_runs_models.PipelineRunStatus.SUCCESS

    mock_send_email = mock.Mock()

    monkeypatch.setattr(
        email_send,
        "send_email",
        mock_send_email,
    )

    pipeline_runs_alerting.send_alert_on_failed_pipeline_run(db, pipeline_run)
    assert mock_send_email.call_count == 0
