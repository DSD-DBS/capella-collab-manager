# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import time
from unittest import mock

import pytest
import responses
from fastapi import testclient
from kubernetes import client as k8s_client
from responses import matchers
from sqlalchemy import orm

import capellacollab.projects.models as project_models
import capellacollab.projects.toolmodels.models as toolmodels_models
from capellacollab.configuration.app import config
from capellacollab.projects.toolmodels.backups import (
    models as pipelines_models,
)
from capellacollab.projects.toolmodels.backups.runs import (
    interface as pipeline_runs_interface,
)
from capellacollab.projects.toolmodels.backups.runs import (
    models as pipeline_runs_models,
)
from capellacollab.sessions.operators import k8s


def test_event_fetching_database(
    db: orm.Session,
    pipeline_run: pipeline_runs_models.DatabasePipelineRun,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that events are fetched correctly and saved in the database.

    To achieve this, we create two mock events, one that was fetched in a previous
    iteration already, another one that is new.
    """
    monkeypatch.setattr(config.k8s.promtail, "loki_enabled", False)

    pod = mock.Mock()
    pod.metadata.name = "pod-name"

    datetime_base = datetime.datetime(2025, 1, 1, 0, 0, 0, tzinfo=datetime.UTC)

    pipeline_run.events_last_fetched_timestamp = datetime_base

    event1 = mock.Mock()
    event1.last_timestamp = datetime_base - datetime.timedelta(hours=1)
    event1.event_time = None
    event1.reason = "Reason"
    event1.message = "This is the message of the event!"

    event2 = mock.Mock()
    event2.last_timestamp = None
    event2.event_time = None
    event2.reason = "Reason"
    event2.message = "This is the message of the event!"

    def mock_get_events_for_involved_object(self, name: str):
        if name == "pod-name":
            return [event1, event2]
        return []

    monkeypatch.setattr(
        k8s.KubernetesOperator,
        "get_events_for_involved_object",
        mock_get_events_for_involved_object,
    )
    monkeypatch.setattr(
        k8s.KubernetesOperator,
        "get_pod_for_job",
        lambda *args, **kwargs: pod,
    )
    pipeline_runs_interface._fetch_events_of_job_run(db, pipeline_run)

    assert len(pipeline_run.logs) == 1
    assert pipeline_run.logs[0].reason == event2.reason
    assert pipeline_run.logs[0].line == event2.message


@responses.activate
def test_event_fetching_loki(
    db: orm.Session,
    pipeline_run: pipeline_runs_models.DatabasePipelineRun,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
):
    """Test that events are fetched correctly and saved in the Grafana Loki."""
    monkeypatch.setattr(config.k8s.promtail, "loki_enabled", True)
    monkeypatch.setattr(
        config.k8s.promtail, "loki_url", "http://localhost:3100/loki/api/v1"
    )
    pod = mock.Mock()
    pod.metadata.name = "pod-name"

    datetime_base = datetime.datetime(2025, 1, 1, 0, 0, 0, tzinfo=datetime.UTC)

    pipeline_run.events_last_fetched_timestamp = (
        datetime_base - datetime.timedelta(minutes=1)
    )

    event1 = mock.Mock()
    event1.last_timestamp = datetime_base - datetime.timedelta(hours=1)
    event1.event_time = None
    event1.reason = "Reason"
    event1.message = "This is the message of the event!"

    event2 = mock.Mock()
    event2.last_timestamp = datetime_base
    event2.event_time = None
    event2.reason = "Reason"
    event2.message = "This is the message of the event!"

    event3 = mock.Mock()
    event3.last_timestamp = datetime_base
    event3.event_time = None
    event3.reason = "Reason"
    event3.message = "This is the message of the event, sent at the same time!"

    def mock_get_events_for_involved_object(self, name: str):
        if name == "pod-name":
            return [event1, event2, event3]
        return []

    monkeypatch.setattr(
        k8s.KubernetesOperator,
        "get_events_for_involved_object",
        mock_get_events_for_involved_object,
    )
    monkeypatch.setattr(
        k8s.KubernetesOperator,
        "get_pod_for_job",
        lambda *args, **kwargs: pod,
    )

    responses.post(
        "http://localhost:3100/loki/api/v1/push",
        match=[
            matchers.json_params_matcher(
                {
                    "streams": [
                        {
                            "stream": {
                                "job_name": "undefined",
                                "pipeline_run_id": str(pipeline_run.id),
                                "log_type": "events",
                            },
                            "values": [
                                [
                                    "1735689600000000000",
                                    'reason="Reason" message="This is the message of the event!"',
                                ],
                                [
                                    "1735689600000000001",
                                    'reason="Reason" message="This is the message of the event, sent at the same time!"',
                                ],
                            ],
                        }
                    ]
                }
            )
        ],
    )

    pipeline_runs_interface._fetch_events_of_job_run(db, pipeline_run)

    # Assure that logs are written to Loki, not to the database
    assert len(pipeline_run.logs) == 0
    assert "ERROR" not in [record.levelname for record in caplog.records]


def test_log_fetching_pending(
    db: orm.Session,
    pipeline_run: pipeline_runs_models.DatabasePipelineRun,
    caplog: pytest.LogCaptureFixture,
):
    """Test that logs are fetched correctly and saved in the database."""
    pipeline_run.status = pipeline_runs_models.PipelineRunStatus.PENDING
    pipeline_runs_interface._fetch_logs_of_job_run(db, pipeline_run)

    assert len(pipeline_run.logs) == 0
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "INFO"


@pytest.mark.usefixtures("freeze_time")
def test_log_fetching_database(
    db: orm.Session,
    pipeline_run: pipeline_runs_models.DatabasePipelineRun,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that logs are fetched correctly and saved in the database."""
    monkeypatch.setattr(config.k8s.promtail, "loki_enabled", False)
    pipeline_run.status = pipeline_runs_models.PipelineRunStatus.RUNNING
    pipeline_run.logs_last_fetched_timestamp = None
    pipeline_run.logs_last_timestamp = None
    pipeline_run.reference_id = "job-name"

    monkeypatch.setattr(
        k8s.KubernetesOperator,
        "get_pod_name_from_job_name",
        lambda *args, **kwargs: "pod-name",
    )
    monkeypatch.setattr(
        k8s_client.CoreV1Api,
        "read_namespaced_pod_log",
        lambda *args, **kwargs: (
            "2025-01-01T08:12:27.716441634Z logline"
            "\n2025-01-01T08:12:27.716441634Z logline2"
            "\nSome message to stderr without timestamp..."
        ),
    )

    pipeline_runs_interface._fetch_logs_of_job_run(db, pipeline_run)

    assert len(pipeline_run.logs) == 3
    assert pipeline_run.logs[0].line == "logline"
    assert pipeline_run.logs[0].timestamp.replace(
        tzinfo=datetime.UTC
    ) == datetime.datetime(2025, 1, 1, 8, 12, 27, 716441, tzinfo=datetime.UTC)
    assert (
        pipeline_run.logs[-1].line
        == "Some message to stderr without timestamp..."
    )
    assert pipeline_run.logs[-1].timestamp.replace(
        tzinfo=datetime.UTC
    ) == datetime.datetime(2025, 2, 1, 9, 1, 27, 0, tzinfo=datetime.UTC)


@pytest.mark.usefixtures("freeze_time")
@responses.activate
def test_log_fetching_loki(
    db: orm.Session,
    pipeline_run: pipeline_runs_models.DatabasePipelineRun,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
):
    """Test that logs are fetched correctly and saved in the Grafana Loki."""
    monkeypatch.setattr(config.k8s.promtail, "loki_enabled", True)
    monkeypatch.setattr(
        config.k8s.promtail, "loki_url", "http://localhost:3100/loki/api/v1"
    )
    pipeline_run.status = pipeline_runs_models.PipelineRunStatus.RUNNING
    pipeline_run.logs_last_fetched_timestamp = None
    pipeline_run.logs_last_timestamp = None
    pipeline_run.reference_id = "job-name"

    monkeypatch.setattr(
        k8s.KubernetesOperator,
        "get_pod_name_from_job_name",
        lambda *args, **kwargs: "pod-name",
    )
    monkeypatch.setattr(
        k8s_client.CoreV1Api,
        "read_namespaced_pod_log",
        lambda *args, **kwargs: (
            "2025-01-01T08:12:27.716441634Z logline"
            "\n2025-01-01T08:12:27.716441634Z logline2"
            "\nSome message to stderr without timestamp..."
        ),
    )

    responses.post(
        "http://localhost:3100/loki/api/v1/push",
        match=[
            matchers.json_params_matcher(
                {
                    "streams": [
                        {
                            "stream": {
                                "job_name": "job-name",
                                "pipeline_run_id": str(pipeline_run.id),
                                "log_type": "logs",
                            },
                            "values": [
                                ["1735719147000000000", "logline"],
                                ["1735719147000000001", "logline2"],
                                [
                                    "1738400487000000000",
                                    "Some message to stderr without timestamp...",
                                ],
                            ],
                        }
                    ]
                }
            )
        ],
    )

    pipeline_runs_interface._fetch_logs_of_job_run(db, pipeline_run)

    # Assure that logs are written to Loki, not to the database
    assert len(pipeline_run.logs) == 0
    assert "ERROR" not in [record.levelname for record in caplog.records]


@responses.activate
def test_get_logs_from_loki(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    pipeline: pipelines_models.DatabasePipeline,
    pipeline_run: pipeline_runs_models.DatabasePipelineRun,
    monkeypatch: pytest.MonkeyPatch,
    client: testclient.TestClient,
):
    """Test that logs are loaded correctly from Grafana Loki."""
    monkeypatch.setattr(config.k8s.promtail, "loki_enabled", True)
    monkeypatch.setattr(
        config.k8s.promtail, "loki_url", "http://localhost:3100/loki/api/v1"
    )

    responses.get(
        "http://localhost:3100/loki/api/v1/query_range",
        json={
            "status": "success",
            "data": {
                "resultType": "streams",
                "result": [
                    {
                        "stream": {
                            "detected_level": "info",
                            "job_name": pipeline_run.reference_id,
                            "log_type": "logs",
                            "pipeline_run_id": pipeline_run.id,
                            "service_name": "unknown_service",
                        },
                        "values": [
                            ["1735719147000000001", "logline2"],
                        ],
                    },
                    {
                        "stream": {
                            "detected_level": "unknown",
                            "job_name": pipeline_run.reference_id,
                            "log_type": "logs",
                            "pipeline_run_id": pipeline_run.id,
                            "service_name": "unknown_service",
                        },
                        "values": [
                            ["1735719147000000000", "logline"],
                            [
                                "1738400487000000000",
                                "logline3",
                            ],
                        ],
                    },
                ],
            },
        },
    )

    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/backups/pipelines/{pipeline.id}/runs/{pipeline_run.id}/logs",
    )

    assert response.status_code == 200
    assert len(response.json()) == 3
    assert response.json()[0]["text"] == "logline"
    assert response.json()[0]["timestamp"] == "2025-01-01T08:12:27Z"
    assert response.json()[1]["text"] == "logline2"
    assert response.json()[2]["text"] == "logline3"


def test_get_logs_from_database(
    db: orm.Session,
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    pipeline: pipelines_models.DatabasePipeline,
    pipeline_run: pipeline_runs_models.DatabasePipelineRun,
    client: testclient.TestClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that logs are loaded correctly from the database."""
    monkeypatch.setattr(config.k8s.promtail, "loki_enabled", False)

    pipeline_run.logs.extend(
        [
            pipeline_runs_models.DatabasePipelineRunLogLine(
                run=pipeline_run,
                line=line,
                timestamp=datetime.datetime(
                    2025, 1, 1, 8, 12, 27, tzinfo=datetime.UTC
                ),
                log_type=pipeline_runs_models.LogType.LOGS,
            )
            for line in ["logline", "logline2", "logline3"]
        ]
    )
    db.commit()

    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/backups/pipelines/{pipeline.id}/runs/{pipeline_run.id}/logs",
    )

    assert response.status_code == 200
    assert len(response.json()) == 3
    assert response.json()[0]["text"] == "logline"
    assert response.json()[0]["timestamp"] == "2025-01-01T08:12:27Z"
    assert response.json()[1]["text"] == "logline2"
    assert response.json()[2]["text"] == "logline3"


@responses.activate
def test_get_events_from_loki(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    pipeline: pipelines_models.DatabasePipeline,
    pipeline_run: pipeline_runs_models.DatabasePipelineRun,
    monkeypatch: pytest.MonkeyPatch,
    client: testclient.TestClient,
):
    """Test that events are loaded correctly from Grafana Loki."""
    monkeypatch.setattr(config.k8s.promtail, "loki_enabled", True)
    monkeypatch.setattr(
        config.k8s.promtail, "loki_url", "http://localhost:3100/loki/api/v1"
    )

    unix_time_in_ns = time.time_ns()

    responses.get(
        "http://localhost:3100/loki/api/v1/query_range",
        json={
            "status": "success",
            "data": {
                "resultType": "streams",
                "result": [
                    {
                        "stream": {
                            "job_name": "bakukcaphvhnftybjthgrztgr",
                            "log_type": "events",
                            "pipeline_run_id": "261",
                            "service_name": "unknown_service",
                            "message": "Created pod: jeybvolmgogsjmmcgwdjvfxuu-x5jxz",
                            "reason": "SuccessfulCreate",
                        },
                        "values": [
                            [
                                unix_time_in_ns,
                                'reason="SuccessfulCreate" message="Created pod: jeybvolmgogsjmmcgwdjvfxuu-x5jxz"',
                            ],
                        ],
                    },
                    {
                        "stream": {
                            "job_name": "bakukcaphvhnftybjthgrztgr",
                            "log_type": "events",
                            "pipeline_run_id": "261",
                            "service_name": "unknown_service",
                            "message": "Started container jeybvolmgogsjmmcgwdjvfxuu",
                            "reason": "Started",
                        },
                        "values": [
                            [
                                unix_time_in_ns + 1,
                                'reason="Started" message="Started container jeybvolmgogsjmmcgwdjvfxuu"',
                            ],
                        ],
                    },
                ],
            },
        },
    )

    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/backups/pipelines/{pipeline.id}/runs/{pipeline_run.id}/events",
    )

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["reason"] == "SuccessfulCreate"
    assert response.json()[1]["reason"] == "Started"


@responses.activate
def test_get_events_from_database(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    pipeline: pipelines_models.DatabasePipeline,
    pipeline_run: pipeline_runs_models.DatabasePipelineRun,
    monkeypatch: pytest.MonkeyPatch,
    client: testclient.TestClient,
    db: orm.Session,
):
    """Test that events are loaded correctly from the database."""
    monkeypatch.setattr(
        config.k8s.promtail,
        "loki_enabled",
        monkeypatch.setattr(config.k8s.promtail, "loki_enabled", False),
    )

    pipeline_run.logs.extend(
        [
            pipeline_runs_models.DatabasePipelineRunLogLine(
                run=pipeline_run,
                line=message,
                reason=reason,
                timestamp=datetime.datetime(
                    2025, 1, 1, 8, 12, 27, tzinfo=datetime.UTC
                ),
                log_type=pipeline_runs_models.LogType.EVENTS,
            )
            for reason, message in [
                (
                    "SuccessfulCreate",
                    "Created pod: jeybvolmgogsjmmcgwdjvfxuu-x5jxz",
                ),
                ("Started", "Started container jeybvolmgogsjmmcgwdjvfxuu"),
            ]
        ]
    )
    db.commit()

    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/backups/pipelines/{pipeline.id}/runs/{pipeline_run.id}/events",
    )

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["reason"] == "SuccessfulCreate"
    assert response.json()[1]["reason"] == "Started"
