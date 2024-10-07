# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest

from capellacollab.settings.modelsources.t4c.license_server import metrics


@pytest.mark.usefixtures("mock_license_server", "t4c_instance")
def test_t4c_used_license_metrics_collector():
    collector = metrics.UsedT4CLicensesCollector()

    data = list(collector.collect())

    sample = data[0].samples[0]
    assert sample.name == "used_t4c_licenses"
    assert sample.value == 1


def test_t4c_used_license_metrics_collector_error():
    collector = metrics.UsedT4CLicensesCollector()

    data = list(collector.collect())

    sample = data[0].samples[0]
    assert sample.name == "used_t4c_licenses"
    assert sample.value == -1


@pytest.mark.usefixtures("mock_license_server", "t4c_instance")
def test_t4c_total_license_metrics_collector():
    collector = metrics.TotalT4CLicensesCollector()

    data = list(collector.collect())

    sample = data[0].samples[0]
    assert sample.name == "total_t4c_licenses"
    assert sample.value == 20


def test_t4c_total_license_metrics_collector_error():
    collector = metrics.TotalT4CLicensesCollector()

    data = list(collector.collect())

    sample = data[0].samples[0]
    assert sample.name == "total_t4c_licenses"
    assert sample.value == -1
