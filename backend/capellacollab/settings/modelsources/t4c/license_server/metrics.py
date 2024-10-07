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
            "Currently used T4C licenses per registered TeamForCapella license server.",
            labels=["license_server_name", "license_server_id"],
        )

        with database.SessionLocal() as db:
            license_servers = crud.get_t4c_license_servers(db)

        if not license_servers:
            return

        for license_server in license_servers:
            try:
                t4c_status = interface.get_t4c_license_server_usage(
                    license_server.usage_api
                )
                used_licenses = t4c_status.total - t4c_status.free
            except Exception:
                used_licenses = -1

            metric.add_metric(
                [license_server.name, str(license_server.id)], used_licenses
            )
        yield metric


class TotalT4CLicensesCollector(prometheus_registry.Collector):
    def collect(self) -> t.Iterable[prometheus_client.core.Metric]:
        metric = prometheus_client.core.GaugeMetricFamily(
            "total_t4c_licenses",
            "Available licenses per registered TeamForCapella license server.",
            labels=["license_server_name", "license_server_id"],
        )

        with database.SessionLocal() as db:
            license_servers = crud.get_t4c_license_servers(db)

        if not license_servers:
            return

        for license_server in license_servers:
            try:
                t4c_status = interface.get_t4c_license_server_usage(
                    license_server.usage_api
                )
                total_licenses = t4c_status.total
            except Exception:
                total_licenses = -1

            metric.add_metric(
                [license_server.name, str(license_server.id)], total_licenses
            )
        yield metric


def register() -> None:
    prometheus_client.REGISTRY.register(UsedT4CLicensesCollector())
    prometheus_client.REGISTRY.register(TotalT4CLicensesCollector())
