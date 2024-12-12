# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import status

from capellacollab.core import exceptions as core_exceptions


class ProjectToolBelongsToOtherProject(core_exceptions.BaseError):
    def __init__(self, project_tool_id: int, project_slug: str):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            title="The project tool belongs to another project",
            reason=f"The project tool with ID {project_tool_id} doesn't belong to the project '{project_slug}'.",
            err_code="PROJECT_TOOL_DOES_NOT_BELONG_TO_PROJECT",
        )

    @classmethod
    def openapi_example(cls) -> "ProjectToolBelongsToOtherProject":
        return cls(-1, "in-flight-entertainment")


class ProjectToolNotFound(core_exceptions.BaseError):
    def __init__(self, project_tool_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            title="Tool not found in project",
            reason=f"The project tool with ID {project_tool_id} was not found.",
            err_code="PROJECT_TOOL_NOT_FOUND",
        )

    @classmethod
    def openapi_example(cls) -> "ProjectToolNotFound":
        return cls(-1)


class ToolAlreadyLinkedToProjectError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            title="Tool already linked to project",
            reason="The specific version of the tool is already linked to the project.",
            err_code="TOOL_ALREADY_EXISTS_IN_PROJECT",
        )

    @classmethod
    def openapi_example(cls) -> "ToolAlreadyLinkedToProjectError":
        return cls()
