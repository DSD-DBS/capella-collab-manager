# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from unittest import mock

import pytest

from capellacollab.projects.toolmodels.backups import (
    interface as pipelines_interface,
)
from capellacollab.projects.toolmodels.backups import (
    models as pipelines_models,
)
from capellacollab.projects.toolmodels.backups.runs import (
    interface as pipeline_runs_interface,
)


def test_run_pipeline_in_kubernetes_without_pipeline(
    caplog: pytest.LogCaptureFixture,
):
    """Test running a pipeline without a valid ID.

    In this case, a logging message is generated, but the application keeps running.
    """
    pipelines_interface.run_pipeline_in_kubernetes(-1)

    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "ERROR"


def test_run_pipeline_in_kubernetes(
    pipeline: pipelines_models.DatabasePipeline,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that a run is properly scheduled when running a pipeline."""

    run_job_mock = mock.Mock()
    monkeypatch.setattr(
        pipeline_runs_interface,
        "run_job_in_kubernetes",
        run_job_mock,
    )

    assert len(pipeline.runs) == 0

    pipelines_interface.run_pipeline_in_kubernetes(pipeline.id)

    assert len(pipeline.runs) == 1
    run_job_mock.assert_called_once_with(pipeline.runs[0].id)
