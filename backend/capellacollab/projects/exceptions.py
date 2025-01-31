# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import status

from capellacollab.core import exceptions as core_exceptions

from . import models


class ProjectNotFoundError(core_exceptions.BaseError):
    def __init__(self, project_slug: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            title="Project not found",
            reason=f"The project with the slug '{project_slug}' was not found.",
            err_code="PROJECT_NOT_FOUND",
        )

    @classmethod
    def openapi_example(cls) -> "ProjectNotFoundError":
        return cls("test")


class ProjectAlreadyExistsError(core_exceptions.BaseError):
    def __init__(self, project_slug: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            title="Project already exists",
            reason=f"The project with the slug '{project_slug}' already exists.",
            err_code="PROJECT_ALREADY_EXISTS",
        )

    @classmethod
    def openapi_example(cls) -> "ProjectAlreadyExistsError":
        return cls("test")


class AssignedModelsPreventDeletionError(
    core_exceptions.ExistingDependenciesError
):
    def __init__(self, project: models.DatabaseProject):
        super().__init__(
            "project",
            project.name,
            [f"Model '{model.slug}'" for model in project.models],
        )

    @classmethod
    def openapi_example(cls) -> "AssignedModelsPreventDeletionError":
        return cls(
            models.DatabaseProject(
                name="test", slug="test", description="example description"
            )
        )
