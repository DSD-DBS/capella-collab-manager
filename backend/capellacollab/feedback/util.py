# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import smtplib
import typing as t
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from sqlalchemy import orm

from capellacollab.config import config
from capellacollab.feedback import exceptions
from capellacollab.feedback.models import AnonymizedSession, Feedback
from capellacollab.settings.configuration import core as config_core
from capellacollab.settings.configuration import (
    models as settings_config_models,
)
from capellacollab.settings.configuration.models import (
    FeedbackAnonymityPolicy,
    FeedbackConfiguration,
)
from capellacollab.users import models as users_models


def format_session(session: AnonymizedSession):
    return f"{session.version.tool.name} ({session.version.name})"


def is_feedback_allowed(db: orm.Session):
    if not config.smtp or not config.smtp.enabled:
        raise exceptions.SmtpNotSetupError()

    cfg = config_core.get_config(db, "global")
    assert isinstance(cfg, settings_config_models.GlobalConfiguration)
    feedback_config = FeedbackConfiguration.model_validate(
        cfg.feedback.model_dump()
    )
    if not feedback_config.enabled:
        raise exceptions.FeedbackNotEnabledError()


def format_email(
    feedback: Feedback,
    user: t.Optional[users_models.DatabaseUser],
    user_agent: str | None,
):
    message = "\n".join(
        [
            f"Rating: {feedback.rating.value}",
            f"Text: {feedback.feedback_text or 'No feedback text provided'}",
            f"User: {f'{user.name} ({user.email})' if user else 'Anonymous User'}",
            f"User Agent: {user_agent or 'Unknown'}",
            f"Feedback Trigger: {feedback.trigger}",
            *[
                session.model_dump_json(indent=2)
                for session in feedback.sessions
            ],
        ]
    )

    if len(feedback.sessions) > 0:
        return {
            "subject": f"New Feedback {feedback.rating.value.capitalize()} for {', '.join([format_session(session) for session in feedback.sessions])}",
            "message": message,
        }
    else:
        return {
            "subject": f"New General Feedback {feedback.rating.value.capitalize()}",
            "message": message,
        }


def send_email(
    feedback: Feedback,
    user: users_models.DatabaseUser,
    user_agent: str | None,
    db: orm.Session,
):
    is_feedback_allowed(db)
    assert config.smtp, "SMTP configuration is not set up"

    cfg = config_core.get_config(db, "global")
    assert isinstance(cfg, settings_config_models.GlobalConfiguration)
    feedback_config = FeedbackConfiguration.model_validate(
        cfg.feedback.model_dump()
    )

    match feedback_config.anonymity_policy:
        case FeedbackAnonymityPolicy.FORCE_ANONYMOUS:
            is_anonymous = True
        case FeedbackAnonymityPolicy.FORCE_IDENTIFIED:
            is_anonymous = False
        case _:
            is_anonymous = not feedback

    email_text = format_email(
        feedback, None if is_anonymous else user, user_agent
    )

    mailserver = smtplib.SMTP(
        config.smtp.host.split(":")[0], int(config.smtp.host.split(":")[1])
    )
    mailserver.ehlo()
    mailserver.starttls()
    mailserver.ehlo()
    mailserver.login(config.smtp.user, config.smtp.password)

    for receiver in feedback_config.receivers:
        msg = MIMEMultipart()
        msg["From"] = config.smtp.sender
        msg["To"] = receiver
        msg["Subject"] = email_text["subject"]
        msg.attach(MIMEText(email_text["message"], "plain"))

        mailserver.sendmail(config.smtp.sender, receiver, msg.as_string())

    mailserver.quit()
