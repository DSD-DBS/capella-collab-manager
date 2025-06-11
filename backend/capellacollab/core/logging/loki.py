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

from capellacollab.configuration.app import config
from capellacollab.configuration.app import models as config_models

from . import exceptions

log = logging.getLogger(__name__)

LOGGING_LEVEL = config.logging.level
PROMTAIL_CONFIGURATION: config_models.K8sPromtailConfig = config.k8s.promtail


class LogEntry(t.TypedDict):
    line: str
    timestamp: datetime.datetime


class RawLogEntry(t.TypedDict):
    line: str
    timestamp: int


def is_loki_activated() -> bool:
    return PROMTAIL_CONFIGURATION.loki_enabled


def check_loki_enabled():
    if not is_loki_activated():
        raise exceptions.GrafanaLokiDisabled()


def _construct_loki_stream_values(entries: list[LogEntry]) -> list[list[str]]:
    values = []
    previous_timestamp_ns: int | None = None
    for entry in entries:
        timestamp_ns = determine_timestamp_in_ns(previous_timestamp_ns, entry)
        values.append(
            [
                str(timestamp_ns),
                entry["line"],
            ]
        )
        previous_timestamp_ns = timestamp_ns

    return values


def determine_timestamp_in_ns(
    previous_timestamp_ns: int | None,
    entry: LogEntry,
) -> int:
    """Increment the timestamp of log entries that have the same timestamp.

    This is used to preserve the order of log entries when they are sent to Loki.
    Simulates the configuration option `increment_duplicate_timestamp` of Loki.
    Since we don't have any control over external Loki instances, we implement this manually.
    https://grafana.com/docs/loki/latest/configure/
    """

    timestamp_ns = int(entry["timestamp"].timestamp()) * 10**9
    if previous_timestamp_ns and previous_timestamp_ns >= timestamp_ns:
        timestamp_ns = previous_timestamp_ns + 1

    return timestamp_ns


def push_logs_to_loki(entries: list[LogEntry], labels) -> None:
    if PROMTAIL_CONFIGURATION.loki_enabled is False:
        return
    assert PROMTAIL_CONFIGURATION.loki_url
    # Convert the streams and labels into the Loki log format
    log_data = json.dumps(
        {
            "streams": [
                {
                    "stream": labels,
                    "values": _construct_loki_stream_values(entries),
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
        log.exception("Error pushing logs to Grafana Loki")
        if e.response:
            log.info("Response from Loki API: %s", e.response.content.decode())


def flatten_loki_streams(event_logs: dict) -> list[RawLogEntry]:
    """Flatten the Loki streams into a list of log lines with timestamps.

    The original nanoseconds timestamp is preserved to enable the sorting of log lines.
    In the later transformation to datetime, the nanoseconds are not preserved.
    """

    return sorted(
        [
            {"timestamp": int(logline[0]), "line": logline[1]}
            for logentry in event_logs
            for logline in logentry["values"]
        ],
        key=lambda log: log["timestamp"],
    )


def fetch_logs_from_loki(
    query,
    start_time: datetime.datetime,
    end_time: datetime.datetime,
):
    if PROMTAIL_CONFIGURATION.loki_enabled is False:
        return None
    assert PROMTAIL_CONFIGURATION.loki_url

    # Prepare the query parameters
    params = {
        "query": query,
        "limit": 5000,
        "start": int(start_time.timestamp()),
        "end": int(end_time.timestamp()),
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
        log.exception("Error fetching logs from Grafana Loki")
        if e.response:
            log.info("Response from Loki API: %s", e.response.content.decode())
        return None
