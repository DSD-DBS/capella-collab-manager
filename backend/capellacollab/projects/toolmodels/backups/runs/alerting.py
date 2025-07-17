# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import logging
import pathlib

import jinja2
from sqlalchemy import orm

from capellacollab.configuration import core as config_core
from capellacollab.configuration.app import config
from capellacollab.core.email import exceptions as email_exceptions
from capellacollab.core.email import models as email_models
from capellacollab.core.email import send as email_send
from capellacollab.projects.toolmodels.backups import (
    interface as backups_interface,
)

from . import models

log = logging.getLogger(__name__)


def send_alert_on_failed_pipeline_run(
    db: orm.Session, run: models.DatabasePipelineRun
) -> None:
    """Send an alert if a pipeline run has failed."""
    if run.status not in [
        models.PipelineRunStatus.TIMEOUT,
        models.PipelineRunStatus.FAILURE,
        models.PipelineRunStatus.UNKNOWN,
    ]:
        return

    cfg = config_core.get_global_configuration(db)
    email_text = format_email(run)

    try:
        email_send.send_email(cfg.alerting.recipients, email_text)
    except email_exceptions.SMTPNotConfiguredError:
        log.info(
            "SMTP not configured, cannot send alert for pipeline run %d",
            run.id,
        )


def format_email(
    pipeline_run: models.DatabasePipelineRun,
) -> email_models.EMailContent:
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(pathlib.Path(__file__).parent),
        autoescape=True,
    )
    template = env.get_template("pipeline_alert.jinja")
    ccm_url = f"{config.general.scheme}://{config.general.host}:{config.general.port}"
    job = backups_interface.get_scheduled_pipeline_job(
        pipeline_run.pipeline.id
    )
    next_run = None
    if job is not None and hasattr(job, "next_run_time") and job.next_run_time:
        next_run = job.next_run_time.astimezone(datetime.UTC)

    html_content = template.render(
        ccm_url=ccm_url,
        pipeline_run=pipeline_run,
        next_run=next_run,
    )

    subject = f"Alert: Pipeline Run {pipeline_run.id} failed (Project {pipeline_run.pipeline.model.project.slug})"
    return email_models.EMailContent(
        subject=subject,
        message=html_content,
        priority=email_models.EMailPriority.HIGHEST,
    )
