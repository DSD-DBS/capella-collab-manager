# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

import prometheus_client
import prometheus_client.core
from prometheus_client import registry as prometheus_registry

from . import engine


class DatabasePoolSizeCollector(prometheus_registry.Collector):
    def collect(self) -> t.Iterable[prometheus_client.core.Metric]:
        metric = prometheus_client.core.GaugeMetricFamily(
            "sqlalchemy_pool_size",
            "SQLAlchemy database connection pool size",
        )

        metric.add_metric([], engine.pool.size())  # type: ignore[attr-defined]

        yield metric


class DatabaseConnectionsInPoolCollector(prometheus_registry.Collector):
    def collect(self) -> t.Iterable[prometheus_client.core.Metric]:
        metric = prometheus_client.core.GaugeMetricFamily(
            "sqlalchemy_connections_in_pool",
            "Available database connections in the SQLAlchemy pool",
        )

        metric.add_metric([], engine.pool.checkedin())  # type: ignore[attr-defined]

        yield metric


class DatabaseOverflowCollector(prometheus_registry.Collector):
    def collect(self) -> t.Iterable[prometheus_client.core.Metric]:
        metric = prometheus_client.core.GaugeMetricFamily(
            "sqlalchemy_pool_overflow",
            "Overflow of the SQLAlchemy database connection pool",
        )

        metric.add_metric([], engine.pool.overflow())  # type: ignore[attr-defined]

        yield metric


class DatabaseCheckedOutConnectionsCollector(prometheus_registry.Collector):
    def collect(self) -> t.Iterable[prometheus_client.core.Metric]:
        metric = prometheus_client.core.GaugeMetricFamily(
            "sqlalchemy_checked_out_connections",
            "Checked out SQLAlchemy database connections",
        )

        metric.add_metric([], engine.pool.checkedout())  # type: ignore[attr-defined]

        yield metric


def register() -> None:
    prometheus_client.REGISTRY.register(DatabasePoolSizeCollector())
    prometheus_client.REGISTRY.register(DatabaseConnectionsInPoolCollector())
    prometheus_client.REGISTRY.register(DatabaseOverflowCollector())
    prometheus_client.REGISTRY.register(
        DatabaseCheckedOutConnectionsCollector()
    )
