# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import status

from capellacollab.core import exceptions as core_exceptions


class ToolVersionNotFoundError(core_exceptions.BaseError):
    def __init__(self, version_id: int):
        self.version_id = version_id
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            title="Tool version not found",
            reason=f"The tool version with id {version_id} was not found.",
            err_code="TOOL_VERSION_NOT_FOUND",
        )


class ToolImageNotFoundError(core_exceptions.BaseError):
    def __init__(self, tool_id: int, image_name: str):
        self.tool_id = tool_id
        self.image_name = image_name
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            title="Tool image not found",
            reason=f"The tool with id {tool_id} doesn't have a {image_name} image.",
            err_code="TOOL_IMAGE_NOT_FOUND",
        )
