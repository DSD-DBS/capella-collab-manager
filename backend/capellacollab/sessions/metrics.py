# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

import prometheus_client
import prometheus_client.core

from capellacollab.core import database
from capellacollab.sessions import crud


class DatabaseSessionsCollector:
    def collect(self) -> t.Iterable[prometheus_client.core.Metric]:
        metric = prometheus_client.core.GaugeMetricFamily(
            "backend_database_sessions",
            "Sessions registered in the backend database",
        )
        with database.SessionLocal() as db:
            metric.add_metric([], crud.count_sessions(db))
        yield metric


def register() -> None:
    prometheus_client.REGISTRY.register(DatabaseSessionsCollector())
