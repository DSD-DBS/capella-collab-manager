# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

import prometheus_client
import prometheus_client.core
from prometheus_client import registry as prometheus_registry

from capellacollab.core import database

from . import crud, interface


class UsedT4CLicensesCollector(prometheus_registry.Collector):
    def collect(self) -> t.Iterable[prometheus_client.core.Metric]:
        metric = prometheus_client.core.GaugeMetricFamily(
            "used_t4c_licenses",
            "Currently used T4C licenses per registered TeamForCapella instance.",
            labels=["instance_name"],
        )

        with database.SessionLocal() as db:
            instances = crud.get_t4c_instances(db)

        if not instances:
            return

        for instance in instances:
            try:
                t4c_status = interface.get_t4c_status(instance)
                used_licenses = t4c_status.total - t4c_status.free
            except Exception:
                used_licenses = -1

            metric.add_metric([instance.name], used_licenses)
        yield metric


class TotalT4CLicensesCollector(prometheus_registry.Collector):
    def collect(self) -> t.Iterable[prometheus_client.core.Metric]:
        metric = prometheus_client.core.GaugeMetricFamily(
            "total_t4c_licenses",
            "Available licenses per registerd TeamForCapella instance.",
            labels=["instance_name"],
        )

        with database.SessionLocal() as db:
            instances = crud.get_t4c_instances(db)

        if not instances:
            return

        for instance in instances:
            try:
                t4c_status = interface.get_t4c_status(instance)
                total_licenses = t4c_status.total
            except Exception:
                total_licenses = -1

            metric.add_metric([instance.name], total_licenses)
        yield metric


def register() -> None:
    prometheus_client.REGISTRY.register(UsedT4CLicensesCollector())
    prometheus_client.REGISTRY.register(TotalT4CLicensesCollector())
