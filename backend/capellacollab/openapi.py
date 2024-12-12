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


def get_all_dependencies(
    dependant: dependencies_models.Dependant,
) -> list[dependencies_models.Dependant]:
    dependencies = []
    for dependency in dependant.dependencies:
        dependencies.append(dependency)
        dependencies.extend(get_all_dependencies(dependency))
    return dependencies


def add_permissions_and_exceptions_to_api_docs(app: fastapi.FastAPI) -> None:
    """Scans all dependencies of routes to add permissions and exceptions to the OpenAPI docs"""

    for route in app.routes:
        if not isinstance(route, routing.APIRoute):
            continue

        authenticated_route = False
        x_required_permissions = None
        x_required_project_permissions = None
        exceptions: list[core_exceptions.BaseError] = []

        for dependency in get_all_dependencies(route.dependant):
            if (
                dependency.call
                and not inspect.isfunction(dependency.call)
                and hasattr(dependency.call, "exceptions")
            ):
                exceptions.extend(dependency.call.exceptions)

            if isinstance(
                dependency.call,
                auth_injectables.AuthenticationInformationValidation,
            ):
                authenticated_route = True

            if isinstance(dependency.call, injectables.PermissionValidation):
                authenticated_route = True
                x_required_permissions = str(dependency.call)

            if isinstance(
                dependency.call,
                projects_permissions_injectables.ProjectPermissionValidation,
            ):
                authenticated_route = True
                x_required_project_permissions = str(dependency.call)

        route.openapi_extra = {
            "x-required-project-permissions": x_required_project_permissions,
            "x-required-permissions": x_required_permissions,
            "security": [{"PersonalAccessToken": [], "Cookie": []}]
            if authenticated_route
            else [],
        }
        if x_required_permissions:
            route.description += (
                "<br /><br />This route requires the following scopes: "
                + str(x_required_permissions)
            )
        if x_required_project_permissions:
            route.description += (
                "<br /><br />This route requires the following project scopes in the corresponding project: "
                + str(x_required_project_permissions)
            )

        if os.getenv("CAPELLACOLLAB_SKIP_OPENAPI_ERROR_RESPONSES", "0") != "1":
            print(route.responses)
            route.responses |= (
                core_responses.translate_exceptions_to_openapi_schema(
                    exceptions
                )
            )
