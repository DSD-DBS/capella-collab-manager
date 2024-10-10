# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

import prometheus_client
import prometheus_client.core
from prometheus_client import registry as prometheus_registry

from capellacollab.core import database

from . import crud, models


class FeedbackCollector(prometheus_registry.Collector):
    def collect(self) -> t.Iterable[prometheus_client.core.Metric]:
        metric = prometheus_client.core.GaugeMetricFamily(
            "feedback_count",
            "Submitted feedback",
            labels=["rating", "anonymous"],
        )

        with database.SessionLocal() as db:
            feedback = crud.count_feedback_by_rating(db)

        for rating in models.FeedbackRating:
            metric.add_metric(
                [str(rating.value), "true"], feedback.get((rating, True), 0)
            )
            metric.add_metric(
                [str(rating.value), "false"], feedback.get((rating, False), 0)
            )

        yield metric


def register() -> None:
    prometheus_client.REGISTRY.register(FeedbackCollector())
