# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import dataclasses

import fastapi
from fastapi import exception_handlers, status


@dataclasses.dataclass
class ExistingDependenciesError(Exception):
    entity_name: str
    entity_type: str
    dependencies: list[str]


async def existing_dependencies_exception_handler(
    request: fastapi.Request, exc: ExistingDependenciesError
) -> fastapi.Response:
    dependencies_str = ", ".join(exc.dependencies)
    return await exception_handlers.http_exception_handler(
        request,
        fastapi.HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "reason": [
                    f"The {exc.entity_type} '{exc.entity_name}' can not be deleted. Please remove the following dependencies first: {dependencies_str}"
                ]
            },
        ),
    )


def register_exceptions(app: fastapi.FastAPI):
    app.add_exception_handler(
        ExistingDependenciesError, existing_dependencies_exception_handler
    )
