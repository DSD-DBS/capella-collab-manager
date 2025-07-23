# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import logging
import pathlib

import jinja2
from sqlalchemy import orm

from capellacollab import scheduling
from capellacollab.configuration import core as config_core
from capellacollab.configuration import models as config_models
from capellacollab.configuration.app import config
from capellacollab.core import database
from capellacollab.core.email import exceptions as email_exceptions
from capellacollab.core.email import models as email_models
from capellacollab.core.email import send as email_send

from . import crud, models

log = logging.getLogger(__name__)


def alert_on_failed_or_pending_sessions():
    """If a session is in an unexpected state, send an alert.

    Unexpected states include:
    - SessionPreparationState is Pending for over 5 minutes
    - SessionState is Pending for over 5 minutes
    - SessionPreparationState or SessionState is Failed
    - SessionState is Terminated
    """
    with database.SessionLocal() as db:
        cfg = config_core.get_global_configuration(db)
        for database_session in crud.get_sessions(db):
            _alert_for_individual_session(
                db=db,
                cfg=cfg,
                database_session=database_session,
            )


def _alert_for_individual_session(
    db: orm.Session,
    database_session: models.DatabaseSession,
    cfg: config_models.GlobalConfiguration,
) -> bool:
    """Send an alert for a specific session if it is in an unexpected state.

    Return True if an alert was sent, False otherwise.
    """

    reason = None
    if database_session.alerted:
        log.debug(
            "Session %s already alerted, skipping.",
            database_session.id,
        )
        return False

    session = models.Session.model_validate(database_session)
    if session.created_at.replace(tzinfo=datetime.UTC) < datetime.datetime.now(
        tz=datetime.UTC
    ) - datetime.timedelta(minutes=5) and (
        session.state == models.SessionState.PENDING
        or session.preparation_state == models.SessionPreparationState.PENDING
    ):
        reason = "The session is pending for over 5 minutes."
    elif (
        session.state == models.SessionState.FAILED
        or session.preparation_state == models.SessionPreparationState.FAILED
    ):
        reason = "The session couldn't be started."
    elif session.state == models.SessionState.TERMINATED:
        reason = "The session was terminated unexpectedly."

    if not reason:
        log.debug(
            "No alert needed for session %s",
            session.id,
        )
        return False

    log.info(
        "Sending alert for session %s, reason: %s",
        session.id,
        reason,
    )

    database_session.alerted = True
    db.commit()

    email = _format_email(
        session=session,
        reason=reason,
    )

    try:
        email_send.send_email(cfg.alerting.recipients, email)
    except email_exceptions.SMTPNotConfiguredError:
        log.info(
            "SMTP not configured, cannot send alert for session %s",
            session.id,
        )
    return True


def _format_email(
    session: models.Session, reason: str
) -> email_models.EMailContent:
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(pathlib.Path(__file__).parent),
        autoescape=True,
    )
    template = env.get_template("session_alert.jinja")
    ccm_url = f"{config.general.scheme}://{config.general.host}:{config.general.port}"

    html_content = template.render(
        session=session,
        reason=reason,
        ccm_url=ccm_url,
        datetime=datetime,
    )

    subject = f"Alert: Session {session.id} in unexpected state"

    return email_models.EMailContent(
        subject=subject,
        message=html_content,
        priority=email_models.EMailPriority.HIGHEST,
    )


def schedule_alerts():  # pragma: no cover
    """Schedule alerts for failed and pending sessions."""
    scheduling.scheduler.add_job(
        alert_on_failed_or_pending_sessions,
        trigger="interval",
        minutes=1,
        id="alert_on_failed_sessions",
        replace_existing=True,
    )
