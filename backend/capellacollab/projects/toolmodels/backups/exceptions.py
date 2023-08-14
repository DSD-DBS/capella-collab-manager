# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import enum

import fastapi
from fastapi import exception_handlers, status


class PipelineOperation(enum.Enum):
    CREATE = "create"
    DELETE = "delete"


class PipelineOperationFailedT4CServerUnreachable(Exception):
    def __init__(self, operation: PipelineOperation):
        self.operation = operation


async def pipeline_creation_failed_t4c_server_unreachable_handler(
    request: fastapi.Request, exc: PipelineOperationFailedT4CServerUnreachable
) -> fastapi.Response:
    return await exception_handlers.http_exception_handler(
        request,
        fastapi.HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "err_code": "PIPELINE_OPERATION_FAILED_T4C_SERVER_UNREACHABLE",
                "title": f"The '{exc.operation.value}' operation on the pipeline failed",
                "reason": (
                    f"We're not able to connect to the TeamForCapella server and therefore cannot {exc.operation.value} the pipeline.",
                    "Please try again later or contact your administrator.",
                ),
            },
        ),
    )


def register_exceptions(app: fastapi.FastAPI):
    app.add_exception_handler(
        PipelineOperationFailedT4CServerUnreachable,
        pipeline_creation_failed_t4c_server_unreachable_handler,
    )
