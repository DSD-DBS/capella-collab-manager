# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime

import apscheduler.schedulers.asyncio as ap_asyncio_scheduler
from apscheduler.executors import pool as ap_executors
from apscheduler.jobstores import sqlalchemy as ap_sqlalchemy

from capellacollab.configuration.app import config
from capellacollab.core.database import engine

jobstores = {"default": ap_sqlalchemy.SQLAlchemyJobStore(engine=engine)}
executors = {
    "default": ap_executors.ThreadPoolExecutor(10),
}

scheduler = ap_asyncio_scheduler.AsyncIOScheduler(
    jobstores=jobstores, executors=executors, timezone=datetime.UTC
)


def start_scheduler() -> None:  # pragma: no cover
    """
    Start the APScheduler with the configured job stores and executors.
    This function should be called at application startup.
    """
    scheduler.start(paused=not config.pipelines.scheduler)


def stop_scheduler() -> None:  # pragma: no cover
    """
    Stop the APScheduler gracefully.
    Wait until all running jobs are finished before shutting down.
    This function should be called at application shutdown.
    """
    scheduler.shutdown()
