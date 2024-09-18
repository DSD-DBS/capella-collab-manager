# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging

from sqlalchemy import orm

from capellacollab.config import config
from capellacollab.core.email import exceptions as email_exceptions
from capellacollab.core.email import models as email_models
from capellacollab.core.email import send as email_send
from capellacollab.settings.configuration import core as config_core
from capellacollab.settings.configuration import (
    models as settings_config_models,
)
from capellacollab.users import models as users_models

from . import exceptions, models


def validate_global_configuration(
    feedback: settings_config_models.FeedbackConfiguration,
):
    if feedback.enabled and not (config.smtp and config.smtp.enabled):
        raise email_exceptions.SMTPNotConfiguredError()

    if feedback.enabled and not feedback.recipients:
        raise exceptions.NoFeedbackRecipientsError()


def disable_feedback(feedback: settings_config_models.FeedbackConfiguration):
    feedback.enabled = False
    feedback.after_session = False
    feedback.on_footer = False
    feedback.on_session_card = False
    feedback.interval.enabled = False


def format_session(session: models.AnonymizedSession):
    return f"{session.version.tool.name} ({session.version.name})"


def check_if_feedback_is_allowed(db: orm.Session):
    if not config.smtp or not config.smtp.enabled:
        raise email_exceptions.SMTPNotConfiguredError()

    cfg = config_core.get_global_configuration(db)
    if not cfg.feedback.enabled:
        raise exceptions.FeedbackNotEnabledError()


def format_email(
    feedback: models.Feedback,
    user: users_models.DatabaseUser | None,
    user_agent: str | None,
) -> email_models.EMailContent:
    rating = feedback.rating.value
    user_msg = user.name if user else "Anonymous"
    if user and user.email:
        user_msg += f" ({user.email})"

    message_list = [
        f"Rating: {rating.capitalize()}",
        f"Text: {feedback.feedback_text or 'No feedback text provided'}",
        f"User: {user_msg}",
        f"User Agent: {user_agent or 'Unknown'}",
    ]
    if feedback.trigger:
        message_list.append(f"Trigger: {feedback.trigger}")
    message_list.append("Sessions:")
    message_list += [
        session.model_dump_json(indent=2) for session in feedback.sessions
    ]

    message_list.append("---")
    message_list.append(
        f"You receive this email because you're registered as feedback recipient in the "
        f"Capella Collaboration Manager ({config.general.scheme}://{config.general.host}:{config.general.port})."
    )
    message_list.append(
        "If you want to unsubscribe, contact your System Administrator."
    )
    message_list.append(
        "Please note that only the user is validated. All other fields are provided via the API and should not be trusted."
    )
    message = "\n".join(message_list)

    if len(feedback.sessions) > 0:
        sessions = ", ".join(
            [format_session(session) for session in feedback.sessions]
        )
        return email_models.EMailContent(
            subject=f"New Feedback with rating {rating} for sessions: {sessions}",
            message=message,
        )
    else:
        return email_models.EMailContent(
            subject=f"New General Feedback with rating {rating}",
            message=message,
        )


def send_feedback_email(
    db: orm.Session,
    feedback: models.Feedback,
    user: users_models.DatabaseUser,
    user_agent: str | None,
    logger: logging.LoggerAdapter,
):
    check_if_feedback_is_allowed(db)
    assert config.smtp  # Already checked in previous function
    cfg = config_core.get_global_configuration(db)

    email_text = format_email(
        feedback, user if feedback.share_contact else None, user_agent
    )

    email_send.send_email(cfg.feedback.recipients, email_text, logger)
