# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import inspect
import os

import fastapi
from fastapi import routing
from fastapi.dependencies import models as dependencies_models

from capellacollab.core import exceptions as core_exceptions
from capellacollab.core import responses as core_responses
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.permissions import injectables
from capellacollab.projects.permissions import (
    injectables as projects_permissions_injectables,
)


def should_skip_openapi_error_responses() -> bool:
    return (
        os.environ.get("CAPELLACOLLAB_SKIP_OPENAPI_ERROR_RESPONSES", "0")
        == "1"
    )


def get_all_dependencies(
    dependant: dependencies_models.Dependant,  # codespell:ignore
) -> list[dependencies_models.Dependant]:  # codespell:ignore
    dependencies = []
    for dependency in dependant.dependencies:  # codespell:ignore dependant
        dependencies.append(dependency)
        dependencies.extend(get_all_dependencies(dependency))
    return dependencies


def add_permissions_and_exceptions_to_api_docs(app: fastapi.FastAPI) -> None:
    """Scans all dependencies of routes to add permissions and exceptions to the OpenAPI docs"""
    for route in app.routes:
        if not isinstance(route, routing.APIRoute):
            continue

        add_openapi_extra_to_route(route)


def derive_permissions_and_dependencies_from_dependencies(
    route: routing.APIRoute,
) -> tuple[bool, list[str], list[str], list[type[core_exceptions.BaseError]]]:
    """Derive permissions and exceptions from dependencies"""

    authenticated_route = False
    x_required_permissions = []
    x_required_project_permissions = []
    exceptions: list[type[core_exceptions.BaseError]] = []

    for dependency in get_all_dependencies(
        route.dependant  # codespell:ignore dependant
    ):
        if (
            dependency.call
            and not inspect.isfunction(dependency.call)
            and hasattr(dependency.call, "exceptions")
        ):
            exceptions.extend(dependency.call.exceptions)

        if isinstance(
            dependency.call,
            auth_injectables._AuthenticationInformationValidation,
        ):
            authenticated_route = True

        if isinstance(dependency.call, injectables.PermissionValidation):
            authenticated_route = True
            x_required_permissions = dependency.call.list_repr()

        if isinstance(
            dependency.call,
            projects_permissions_injectables.ProjectPermissionValidation,
        ):
            authenticated_route = True
            x_required_project_permissions = dependency.call.list_repr()

    return (
        authenticated_route,
        x_required_permissions,
        x_required_project_permissions,
        exceptions,
    )


def add_openapi_extra_to_route(route: routing.APIRoute) -> None:
    (
        authenticated_route,
        x_required_permissions,
        x_required_project_permissions,
        exceptions,
    ) = derive_permissions_and_dependencies_from_dependencies(route)

    route.openapi_extra = {
        "x-required-project-permissions": x_required_project_permissions,
        "x-required-permissions": x_required_permissions,
        "security": [{"PersonalAccessToken": [], "Cookie": []}]
        if authenticated_route
        else [],
    }
    if x_required_permissions:
        if route.description:
            route.description += "<br /><br />"
        route.description += (
            "This route requires the following permissions: "
            + ", ".join([f"`{perm}`" for perm in x_required_permissions])
        )
    if x_required_project_permissions:
        if route.description:
            route.description += "<br /><br />"
        route.description += (
            "This route requires the following permissions in the corresponding project: "
            + ", ".join(
                [f"`{perm}`" for perm in x_required_project_permissions]
            )
        )

    if not should_skip_openapi_error_responses():
        route.responses |= (
            core_responses.translate_exceptions_to_openapi_schema(exceptions)
        )


def get_all_subclasses(
    cls: type[core_exceptions.BaseError],
) -> list[type[core_exceptions.BaseError]]:
    """Get all subclasses recursively"""
    all_subclasses = []

    for subclass in cls.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(get_all_subclasses(subclass))

    return all_subclasses


def get_exception_schemas():
    if should_skip_openapi_error_responses():
        return {}

    schemas = {}
    for exc in get_all_subclasses(core_exceptions.BaseError):  # type: ignore
        example = exc.openapi_example()
        if not example:
            continue
        schemas[exc.__name__] = {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Descriptive title of the error.",
                    "example": example.title,
                },
                "reason": {
                    "type": "string",
                    "description": "Reason for the error and any possible resolutions / next steps.",
                    "example": example.reason,
                },
                "err_code": {
                    "type": "string",
                    "description": (
                        "Unique error code."
                        "It can be used to identify a specific error, or for filtering in the logs."
                    ),
                    "example": example.err_code,
                },
            },
            "required": ["title", "reason", "err_code"],
        }
    return schemas
