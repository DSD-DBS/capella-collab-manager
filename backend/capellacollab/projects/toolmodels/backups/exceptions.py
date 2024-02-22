# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import enum

from fastapi import status

from capellacollab.core import exceptions as core_exceptions


class PipelineOperation(enum.Enum):
    CREATE = "create"
    DELETE = "delete"


class PipelineOperationFailedT4CServerUnreachable(core_exceptions.BaseError):
    def __init__(self, operation: PipelineOperation):
        self.operation = operation
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            title=f"The '{operation.value}' operation on the pipeline failed",
            reason=(
                f"We're not able to connect to the TeamForCapella server and therefore cannot {operation.value} the pipeline. "
                "Please try again later or contact your administrator."
            ),
            err_code="PIPELINE_OPERATION_FAILED_T4C_SERVER_UNREACHABLE",
        )
