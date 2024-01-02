# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import dataclasses

import fastapi
from fastapi import exception_handlers, status

from capellacollab.core import exceptions as core_exceptions


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


@dataclasses.dataclass
class T4CInstanceWithNameAlreadyExistsError(
    core_exceptions.ResourceAlreadyExistsError
):
    def __init__(self):
        super().__init__(resource_name="T4C Instance", identifier_name="name")


def register_exceptions(app: fastapi.FastAPI):
    app.add_exception_handler(
        T4CInstanceIsArchivedError, t4c_instance_is_archived_exception_handler  # type: ignore[arg-type]
    )
    app.add_exception_handler(
        T4CInstanceWithNameAlreadyExistsError,
        core_exceptions.resource_already_exists_exception_handler,  # type: ignore[arg-type]
    )
