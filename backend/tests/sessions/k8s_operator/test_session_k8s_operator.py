# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import datetime

import pytest
from kubernetes import client
from kubernetes.client import exceptions

from capellacollab.sessions import models as sessions_models
from capellacollab.sessions.operators import k8s
from capellacollab.tools import models as tools_models


def test_start_session(monkeypatch: pytest.MonkeyPatch):
    operator = k8s.KubernetesOperator()

    name = "testname"
    creation_timestamp = datetime.datetime.now(tz=datetime.UTC)

    pod_counter = 0
    service_counter = 0
    disruption_budget_counter = 0

    # pylint: disable=unused-argument
    def create_namespaced_pod(namespace, deployment):
        nonlocal pod_counter
        pod_counter += 1
        return client.V1Pod(
            metadata=client.V1ObjectMeta(
                name=name, creation_timestamp=creation_timestamp
            )
        )

    monkeypatch.setattr(
        operator.v1_core,
        "create_namespaced_pod",
        create_namespaced_pod,
    )

    # pylint: disable=unused-argument
    def create_namespaced_service(namespace, service):
        nonlocal service_counter
        service_counter += 1
        return client.V1Service(metadata=client.V1ObjectMeta(name=name))

    monkeypatch.setattr(
        operator.v1_core,
        "create_namespaced_service",
        create_namespaced_service,
    )

    def create_namespaced_pod_disruption_budget(namespace, budget):
        nonlocal disruption_budget_counter
        disruption_budget_counter += 1

    monkeypatch.setattr(
        operator.v1_policy,
        "create_namespaced_pod_disruption_budget",
        create_namespaced_pod_disruption_budget,
    )

    tool = tools_models.DatabaseTool(name="testtool")
    session = operator.start_session(
        session_id="jdlöfajödfjnasdf",
        image="hello-world",
        username="testuser",
        session_type=sessions_models.SessionType.PERSISTENT,
        tool=tool,
        environment={},
        init_environment={},
        ports={"rdp": 3389},
        volumes=[],
        init_volumes=[],
        labels={},
        annotations={},
    )

    assert pod_counter == 1
    assert service_counter == 1
    assert disruption_budget_counter == 1

    assert session["id"] == "testname"


def test_kill_session(monkeypatch: pytest.MonkeyPatch):
    operator = k8s.KubernetesOperator()

    monkeypatch.setattr(
        operator.v1_core,
        "delete_namespaced_pod",
        lambda namespace, name: client.V1Status(),
    )

    monkeypatch.setattr(
        operator.v1_core,
        "delete_namespaced_service",
        lambda namespace, name: client.V1Status(),
    )

    monkeypatch.setattr(
        operator.v1_policy,
        "delete_namespaced_pod_disruption_budget",
        lambda namespace, name: client.V1Status(),
    )

    operator.kill_session("testname")


def test_create_job(monkeypatch: pytest.MonkeyPatch):
    operator = k8s.KubernetesOperator()
    monkeypatch.setattr(
        operator.v1_batch, "create_namespaced_job", lambda namespace, job: None
    )
    result = operator.create_job(
        image="fakeimage",
        command="fakecmd",
        labels={"key": "value"},
        environment={"ENVVAR": "value"},
        tool_resources=tools_models.Resources(),
    )

    assert result


def test_create_cronjob(monkeypatch: pytest.MonkeyPatch):
    operator = k8s.KubernetesOperator()
    monkeypatch.setattr(
        operator.v1_batch,
        "create_namespaced_cron_job",
        lambda namespace, job: None,
    )
    result = operator.create_cronjob(
        image="fakeimage",
        command="fakecmd",
        environment={"ENVVAR": "value"},
        labels={},
        tool_resources=tools_models.Resources(),
    )

    assert result


def test_delete_disruption_budget_with_api_error(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that _delete_disruptionbudget does not raise an exception if the
    Pod disruption budget does not exist.
    """

    operator = k8s.KubernetesOperator()

    def raise_api_exception(*args, **kwargs):
        raise exceptions.ApiException(status=404)

    monkeypatch.setattr(
        operator.v1_policy,
        "delete_namespaced_pod_disruption_budget",
        raise_api_exception,
    )
    result = operator._delete_disruptionbudget("testname")
    assert result is None
