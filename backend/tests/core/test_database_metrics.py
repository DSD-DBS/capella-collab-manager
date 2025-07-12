# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from capellacollab.core.database import metrics as database_metrics


def test_sqlalchemy_pool_size_metric():
    data = list(database_metrics.DatabasePoolSizeCollector().collect())

    assert data[0].samples[0].value == 20


def test_sqlalchemy_connections_in_pool_metric():
    data = list(
        database_metrics.DatabaseConnectionsInPoolCollector().collect()
    )

    assert data[0].samples[0].value is not None


def test_sqlalchemy_pool_overflow_metric():
    data = list(database_metrics.DatabaseOverflowCollector().collect())

    assert data[0].samples[0].value is not None


def test_sqlalchemy_checked_out_connections_metric():
    data = list(
        database_metrics.DatabaseCheckedOutConnectionsCollector().collect()
    )

    assert data[0].samples[0].value == 0
