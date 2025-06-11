# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Update pipelines for scheduling

Revision ID: 53b8f1f94922
Revises: 169c90c7eff1
Create Date: 2025-06-27 14:56:02.952043

"""

import http
import logging

import sqlalchemy as sa
from alembic import op
from apscheduler.triggers import cron as ap_cron_trigger
from kubernetes.client import exceptions as k8s_exceptions
from sqlalchemy import orm

from capellacollab import scheduling
from capellacollab.configuration import core as configuration_core
from capellacollab.projects.toolmodels.backups import (
    interface as pipeline_interface,
)
from capellacollab.sessions.operators import k8s

# revision identifiers, used by Alembic.
revision = "53b8f1f94922"
down_revision = "169c90c7eff1"
branch_labels = None
depends_on = None

log = logging.getLogger(__name__)


def delete_cronjob(_id: str):
    operator = k8s.KubernetesOperator()

    try:
        operator.v1_batch.delete_namespaced_cron_job(
            namespace=k8s.namespace, name=_id
        )
    except k8s_exceptions.ApiException as e:
        # Cronjob doesn't exist or was already deleted
        # Nothing to do
        if e.status == http.HTTPStatus.NOT_FOUND:
            return
        raise


def create_job(db: orm.Session, pipeline_id: int):
    pipeline_config = configuration_core.get_global_configuration(db).pipelines
    scheduling.scheduler.add_job(
        pipeline_interface.run_pipeline_in_kubernetes,
        trigger=ap_cron_trigger.CronTrigger.from_crontab(
            pipeline_config.cron, timezone=pipeline_config.timezone
        ),
        args=[pipeline_id],
        id=f"pipeline-{pipeline_id}",
        name=f"Pipeline {pipeline_id}",
        coalesce=True,
        misfire_grace_time=pipeline_config.misfire_grace_time,
    )


def upgrade():
    connection = op.get_bind()
    session = sa.orm.sessionmaker()(bind=connection)

    t_backups = sa.Table("backups", sa.MetaData(), autoload_with=op.get_bind())
    backups = op.get_bind().execute(sa.select(t_backups))

    for backup in backups:
        if backup.run_nightly and backup.k8s_cronjob_id:
            log.warning(
                "Backup %s is configured to run nightly. Replacing the cronjob '%s' with the new scheduling system.",
                backup.id,
                backup.k8s_cronjob_id,
            )
            delete_cronjob(backup.k8s_cronjob_id)
            create_job(session, backup.id)

    # Now proceed with dropping the columns
    op.drop_column("backups", "include_commit_history")
    op.drop_column("backups", "k8s_cronjob_id")
    op.alter_column(
        "pipeline_run",
        "triggerer_id",
        existing_type=sa.INTEGER(),
        nullable=True,
    )
