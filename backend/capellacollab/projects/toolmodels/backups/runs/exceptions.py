# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import status

from capellacollab.core import exceptions as core_exceptions


class PipelineRunBelongsToOtherPipelineError(core_exceptions.BaseError):
    def __init__(self, pipeline_run_id: int, pipeline_id: int):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            title="Pipeline run belongs to other pipeline",
            reason=f"The pipeline run with the ID {pipeline_run_id} doesn't belong to the pipeline with ID {pipeline_id}.",
            err_code="PIPELINE_RUN_BELONGS_TO_OTHER_PIPELINE",
        )

    @classmethod
    def openapi_example(cls) -> "PipelineRunBelongsToOtherPipelineError":
        return cls(-1, -1)


class PipelineRunNotFoundError(core_exceptions.BaseError):
    def __init__(self, pipeline_run_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            title="Pipeline run not found",
            reason=f"The pipeline run with the ID {pipeline_run_id} was not found.",
            err_code="PIPELINE_RUN_NOT_FOUND",
        )

    @classmethod
    def openapi_example(cls) -> "PipelineRunNotFoundError":
        return cls(-1)
