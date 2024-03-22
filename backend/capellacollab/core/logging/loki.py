# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import http
import json
import logging
import logging.handlers
import typing as t

import requests
from requests import auth

from capellacollab.config import config
from capellacollab.config import models as config_models

from . import exceptions

LOGGING_LEVEL = config.logging.level
PROMTAIL_CONFIGURATION: config_models.K8sPromtailConfig = config.k8s.promtail


class LogEntry(t.TypedDict):
    line: str
    timestamp: datetime.datetime


def push_logs_to_loki(entries: list[LogEntry], labels):
    # Convert the streams and labels into the Loki log format
    log_data = json.dumps(
        {
            "streams": [
                {
                    "stream": labels,
                    "values": [
                        [
                            str(int(entry["timestamp"].timestamp()) * 10**9),
                            entry["line"],
                        ]
                        for entry in entries
                    ],
                }
            ]
        }
    )

    # Send the log data to Loki
    try:
        response = requests.post(
            PROMTAIL_CONFIGURATION.loki_url + "/push",
            data=log_data,
            headers={"Content-Type": "application/json"},
            auth=auth.HTTPBasicAuth(
                PROMTAIL_CONFIGURATION.loki_username,
                PROMTAIL_CONFIGURATION.loki_password,
            ),
            timeout=10,
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.exception("Error pushing logs to Grafana Loki", exc_info=True)
        logging.info("Response from Loki API: %s", e.response.content.decode())


def fetch_logs_from_loki(
    query,
    start_time: datetime.datetime,
    end_time: datetime.datetime,
):
    # Prepare the query parameters
    params = {
        "query": query,
        "limit": 5000,
        "start": int(start_time.timestamp()),  # Convert to milliseconds
        "end": int(end_time.timestamp()),  # Convert to milliseconds
        "direction": "forward",
    }

    # Send the query request to Loki
    try:
        response = requests.get(
            PROMTAIL_CONFIGURATION.loki_url + "/query_range",
            params=params,
            headers={"Content-Type": "application/json"},
            auth=auth.HTTPBasicAuth(
                PROMTAIL_CONFIGURATION.loki_username,
                PROMTAIL_CONFIGURATION.loki_password,
            ),
            timeout=5,
        )

        if response.status_code == http.HTTPStatus.TOO_MANY_REQUESTS:
            raise exceptions.TooManyOutStandingRequests

        response.raise_for_status()
        logs = response.json()
        return logs["data"]["result"]
    except requests.exceptions.RequestException as e:
        logging.exception(
            "Error fetching logs from Grafana Loki", exc_info=True
        )
        logging.info("Response from Loki API: %s", e.response.content.decode())
        return None
