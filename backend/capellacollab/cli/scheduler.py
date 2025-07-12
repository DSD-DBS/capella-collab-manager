# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging

import typer
from apscheduler import events as ap_events

logging.getLogger("apscheduler").setLevel(logging.WARNING)

from . import logging as _logging

app = typer.Typer(help="Manage the integrated scheduler.")

LOGGER = logging.getLogger(__name__)


def scheduler_heartbeat():  # pragma: no cover
    pass  # No operation, just to wake up the scheduler


def event_listener(event: ap_events.JobEvent):  # pragma: no cover
    """Listen to job events and log them.

    All events can be found here:
    https://apscheduler.readthedocs.io/en/latest/modules/events.html
    """

    if (
        not isinstance(event, ap_events.JobEvent)
        or event.job_id == "scheduler_heartbeat"
    ):
        return

    match event.code:
        case ap_events.EVENT_JOB_ADDED:
            LOGGER.info(
                "Job %s was added for scheduling.",
                event.job_id,
            )
        case ap_events.EVENT_JOB_REMOVED:
            LOGGER.info("Job %s was removed from the scheduler.", event.job_id)
        case ap_events.EVENT_JOB_MODIFIED:
            LOGGER.info(
                "Job %s was modified. It may have been rescheduled.",
                event.job_id,
            )
        case ap_events.EVENT_JOB_SUBMITTED:
            assert isinstance(event, ap_events.JobSubmissionEvent)
            formatted_times = ", ".join(
                rt.strftime("%Y-%m-%d %H:%M:%S %Z")
                for rt in event.scheduled_run_times
            )
            LOGGER.info(
                "Job %s submitted to the executor successfully and is scheduled to run at %s.",
                event.job_id,
                formatted_times,
            )
        case ap_events.EVENT_JOB_MAX_INSTANCES:
            LOGGER.warning(
                "Job %s reached maximum instances. It may not be able to run.",
                event.job_id,
            )
        case ap_events.EVENT_JOB_EXECUTED:
            LOGGER.info("Job %s executed successfully.", event.job_id)
        case ap_events.EVENT_JOB_ERROR:
            assert isinstance(event, ap_events.JobExecutionEvent)
            LOGGER.error(
                "Job %s encountered an error with exception '%s'.",
                event.job_id,
                event.exception,
            )
        case ap_events.EVENT_JOB_MISSED:
            LOGGER.warning(
                "Job %s was missed. It may not have been scheduled correctly.",
                event.job_id,
            )


@app.command(help="Run the scheduler and trigger to schedule jobs.")
def run(
    _verbose: _logging.VerboseOption = False,
):  # pragma: no cover
    from apscheduler.schedulers import background as ap_background_scheduler

    from capellacollab import core, scheduling
    from capellacollab.configuration.app import config

    if core.LOCAL_DEVELOPMENT_MODE:
        LOGGER.warning(
            "To avoid scheduler interruptions, the scheduler will not auto-reload on backend changes."
            " After applying changes, please restart the scheduler manually."
        )

    if config.pipelines.scheduler:
        LOGGER.warning(
            "The scheduler is enabled via the `pipeline.scheduler` configuration. "
            " This means that the scheduler will run as part of the backend process."
            " Since you are running the scheduler separately, it's recommended to disable the integrated scheduler in the configuration to avoid scheduler conflicts."
        )

    scheduler = ap_background_scheduler.BlockingScheduler(
        jobstores=scheduling.jobstores
    )

    try:
        scheduler.add_listener(
            event_listener,
            ap_events.EVENT_ALL,
        )
        scheduler.add_job(
            scheduler_heartbeat,
            trigger="interval",
            seconds=1,
            id="scheduler_heartbeat",
            replace_existing=True,
        )
        typer.secho(
            "Starting scheduler... Press Ctrl+C to stop.",
            fg=typer.colors.GREEN,
        )
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        typer.secho(
            "\nShutting down scheduler gracefully...", fg=typer.colors.YELLOW
        )
    finally:
        scheduler.shutdown()
