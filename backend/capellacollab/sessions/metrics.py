# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import itertools
import os
import typing as t

import prometheus_client
import prometheus_client.core
from prometheus_client import registry as prometheus_registry

from capellacollab.core import database

from . import crud, operators


class DatabaseSessionsCollector(prometheus_registry.Collector):
    def collect(self) -> t.Iterable[prometheus_client.core.Metric]:
        metric = prometheus_client.core.GaugeMetricFamily(
            "backend_database_sessions",
            "Sessions registered in the backend database",
        )
        with database.SessionLocal() as db:
            metric.add_metric([], crud.count_sessions(db))
        yield metric

    def describe(self) -> t.Iterable[prometheus_client.core.Metric]:
        yield prometheus_client.core.GaugeMetricFamily(
            "backend_database_sessions",
            "Sessions registered in the backend database",
        )


class DeployedSessionsCollector(prometheus_registry.Collector):
    def collect(self) -> t.Iterable[prometheus_client.core.Metric]:
        metric = prometheus_client.core.GaugeMetricFamily(
            "backend_deployed_sessions",
            "Sessions running in the sessions namespace",
            labels=("workload", "phase"),
        )
        operator = operators.get_operator()
        pods = operator.get_pods(
            label_selector="capellacollab/workload=session"
        )
        statuses = []
        for pod in pods:
            labels = pod.metadata.labels
            if labels is None or "workload" not in labels:
                continue

            statuses.append((labels["workload"], pod.status.phase.lower()))
        for labels, g in itertools.groupby(statuses):
            metric.add_metric(labels, len(list(g)))
        yield metric

    def describe(self) -> t.Iterable[prometheus_client.core.Metric]:
        yield prometheus_client.core.GaugeMetricFamily(
            "backend_deployed_sessions",
            "Sessions running in the sessions namespace",
            labels=("workload", "phase"),
        )


def register() -> None:
    if os.getenv("DISABLE_SESSION_COLLECTOR", "") not in ("true", "1", "t"):
        prometheus_client.REGISTRY.register(DatabaseSessionsCollector())
        prometheus_client.REGISTRY.register(DeployedSessionsCollector())
