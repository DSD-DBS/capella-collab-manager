# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from fastapi import exception_handlers, status


class T4CInstanceIsArchivedError(Exception):
    def __init__(self, t4c_instance_id: int):
        self.t4c_instance_id = t4c_instance_id


async def t4c_instance_is_archived_exception_handler(
    request: fastapi.Request, exc: T4CInstanceIsArchivedError
) -> fastapi.Response:
    return await exception_handlers.http_exception_handler(
        request,
        fastapi.HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "reason": f"The T4C instance identified by {exc.t4c_instance_id} is archived, thus prohibiting the execution of the requested operation."
            },
        ),
    )


def register_exceptions(app: fastapi.FastAPI):
    app.add_exception_handler(
        T4CInstanceIsArchivedError, t4c_instance_is_archived_exception_handler
    )
