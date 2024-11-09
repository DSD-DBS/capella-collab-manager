# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from kubernetes import client

from capellacollab.sessions import models as sessions_models
from capellacollab.sessions import operators


@pytest.fixture(
    name="init_container_status",
)
def fixture_init_container_status(
    request: pytest.FixtureRequest,
) -> client.V1ContainerState:
    return request.param


@pytest.fixture(
    name="container_status",
)
def fixture_container_status(
    request: pytest.FixtureRequest,
) -> client.V1ContainerState:
    return request.param


@pytest.fixture(
    name="expected",
)
def fixture_expected(
    request: pytest.FixtureRequest,
) -> tuple[
    sessions_models.SessionPreparationState, sessions_models.SessionState
]:
    return request.param


@pytest.fixture(name="pod")
def fixture_pod(
    init_container_status: client.V1ContainerState,
    container_status: client.V1ContainerState,
    monkeypatch: pytest.MonkeyPatch,
) -> client.V1Pod:
    pod = client.V1Pod(
        status=client.V1PodStatus(
            container_statuses=[
                client.V1ContainerStatus(
                    name="session",
                    state=container_status,
                    image="hello-world",
                    image_id="hello-world",
                    ready=True,
                    restart_count=0,
                ),
            ],
            init_container_statuses=[
                client.V1ContainerStatus(
                    name="session-preparation",
                    state=init_container_status,
                    image="hello-world",
                    image_id="hello-world",
                    ready=True,
                    restart_count=0,
                ),
            ],
        ),
    )

    monkeypatch.setattr(
        client.CoreV1Api,
        "list_namespaced_pod",
        lambda *args, **kwargs: client.V1PodList(items=[pod]),
    )


@pytest.mark.parametrize(
    "init_container_status, container_status, expected",
    [
        (
            client.V1ContainerState(
                running=None, terminated=None, waiting=None
            ),
            client.V1ContainerState(
                running=None, terminated=None, waiting=None
            ),
            (
                sessions_models.SessionPreparationState.UNKNOWN,
                sessions_models.SessionState.UNKNOWN,
            ),
        ),
        (
            client.V1ContainerState(
                running=None,
                terminated=None,
                waiting=client.V1ContainerStateWaiting(
                    reason="ContainerCreating"
                ),
            ),
            client.V1ContainerState(
                running=None,
                terminated=None,
                waiting=client.V1ContainerStateWaiting(
                    reason="PodInitializing"
                ),
            ),
            (
                sessions_models.SessionPreparationState.PENDING,
                sessions_models.SessionState.PENDING,
            ),
        ),
        (
            client.V1ContainerState(
                running=True, terminated=None, waiting=None
            ),
            client.V1ContainerState(
                running=None,
                terminated=None,
                waiting=client.V1ContainerStateWaiting(
                    reason="PodInitializing"
                ),
            ),
            (
                sessions_models.SessionPreparationState.RUNNING,
                sessions_models.SessionState.PENDING,
            ),
        ),
        (
            client.V1ContainerState(
                running=None,
                terminated=client.V1ContainerStateTerminated(
                    reason="Error", exit_code=1
                ),
                waiting=None,
            ),
            client.V1ContainerState(
                running=None,
                terminated=None,
                waiting=client.V1ContainerStateWaiting(
                    reason="PodInitializing"
                ),
            ),
            (
                sessions_models.SessionPreparationState.FAILED,
                sessions_models.SessionState.PENDING,
            ),
        ),
        (
            client.V1ContainerState(
                running=None,
                terminated=client.V1ContainerStateTerminated(
                    reason="Completed", exit_code=0
                ),
                waiting=None,
            ),
            client.V1ContainerState(
                running=None,
                terminated=None,
                waiting=client.V1ContainerStateWaiting(
                    reason="ContainerCreating"
                ),
            ),
            (
                sessions_models.SessionPreparationState.COMPLETED,
                sessions_models.SessionState.PENDING,
            ),
        ),
        (
            client.V1ContainerState(
                running=None,
                terminated=client.V1ContainerStateTerminated(
                    reason="Completed", exit_code=0
                ),
                waiting=None,
            ),
            client.V1ContainerState(
                running=None,
                terminated=None,
                waiting=client.V1ContainerStateWaiting(
                    reason="ImagePullBackOff"
                ),
            ),
            (
                sessions_models.SessionPreparationState.COMPLETED,
                sessions_models.SessionState.FAILED,
            ),
        ),
        (
            client.V1ContainerState(
                running=None,
                terminated=client.V1ContainerStateTerminated(
                    reason="Completed", exit_code=0
                ),
                waiting=None,
            ),
            client.V1ContainerState(
                running=True, terminated=None, waiting=None
            ),
            (
                sessions_models.SessionPreparationState.COMPLETED,
                sessions_models.SessionState.RUNNING,
            ),
        ),
        (
            client.V1ContainerState(
                running=None,
                terminated=client.V1ContainerStateTerminated(
                    reason="Completed", exit_code=0
                ),
                waiting=None,
            ),
            client.V1ContainerState(
                running=None, terminated=True, waiting=None
            ),
            (
                sessions_models.SessionPreparationState.COMPLETED,
                sessions_models.SessionState.TERMINATED,
            ),
        ),
    ],
)
@pytest.mark.usefixtures("pod")
def test_session_state(
    expected: tuple[
        sessions_models.SessionPreparationState, sessions_models.SessionState
    ]
):
    assert operators.get_operator().get_session_state("test") == expected


def test_session_state_not_found(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        client.CoreV1Api,
        "list_namespaced_pod",
        lambda *args, **kwargs: client.V1PodList(items=[]),
    )

    assert operators.get_operator().get_session_state("test") == (
        sessions_models.SessionPreparationState.NOT_FOUND,
        sessions_models.SessionState.NOT_FOUND,
    )
