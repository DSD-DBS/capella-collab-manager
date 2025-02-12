# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import pathlib

import jinja2
from sqlalchemy import orm

from capellacollab.configuration import core as config_core
from capellacollab.configuration import models as settings_config_models
from capellacollab.configuration.app import config
from capellacollab.core.email import exceptions as email_exceptions
from capellacollab.core.email import models as email_models
from capellacollab.core.email import send as email_send
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
    user: users_models.User | None,
    user_agent: str | None,
) -> email_models.EMailContent:
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(pathlib.Path(__file__).parent),
        autoescape=True,
    )
    template = env.get_template("email.jinja")
    ccm_url = f"{config.general.scheme}://{config.general.host}:{config.general.port}"

    html_content = template.render(
        feedback=feedback, user=user, user_agent=user_agent, ccm_url=ccm_url
    )

    if feedback.sessions:
        sessions = ", ".join(
            format_session(session) for session in feedback.sessions
        )
        subject = f"New Feedback with rating {feedback.rating.value} for sessions: {sessions}"
    else:
        subject = f"New General Feedback with rating {feedback.rating.value}"

    return email_models.EMailContent(subject=subject, message=html_content)


def send_feedback_email(
    db: orm.Session,
    feedback: models.Feedback,
    user: users_models.User | None,
    user_agent: str | None,
    logger: logging.LoggerAdapter,
):
    check_if_feedback_is_allowed(db)
    assert config.smtp  # Already checked in previous function
    cfg = config_core.get_global_configuration(db)

    try:
        email_text = format_email(feedback, user, user_agent)
    except Exception:
        logger.exception("Error while formatting email.")
        raise

    email_send.send_email(cfg.feedback.recipients, email_text, logger)
