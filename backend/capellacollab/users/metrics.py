# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

import prometheus_client
import prometheus_client.core
from prometheus_client import registry as prometheus_registry

from capellacollab.core import database

from . import crud


class UserCountCollector(prometheus_registry.Collector):
    def collect(self) -> t.Iterable[prometheus_client.core.Metric]:
        metric = prometheus_client.core.GaugeMetricFamily(
            "user_count",
            "Amount of registered users",
            labels=["beta"],
        )

        with database.SessionLocal() as db:
            users = crud.count_users_by_beta(db)

        metric.add_metric(["true"], users.get(True, 0))
        metric.add_metric(["false"], users.get(False, 0))

        yield metric

    def describe(self) -> t.Iterable[prometheus_client.core.Metric]:
        yield prometheus_client.core.GaugeMetricFamily(
            "user_count",
            "Amount of registered users",
            labels=["beta"],
        )


def register() -> None:
    prometheus_client.REGISTRY.register(UserCountCollector())
