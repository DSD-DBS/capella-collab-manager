# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import status

from capellacollab.core import exceptions as core_exceptions


class VersionIdNotSetError(core_exceptions.BaseError):
    def __init__(self, toolmodel_id: int):
        self.toolmodel_id = toolmodel_id
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            title="Toolmodel version not set",
            reason=f"The toolmodel with id {toolmodel_id} does not have a version set.",
            err_code="VERSION_ID_NOT_SET",
        )


class ToolModelNotFound(core_exceptions.BaseError):
    def __init__(self, project_slug: str, model_slug: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            title="Toolmodel not found",
            reason=f"The model with the slug '{model_slug}' of the project '{project_slug}' was not found.",
            err_code="TOOLMODEL_NOT_FOUND",
        )


class ToolModelAlreadyExistsError(core_exceptions.BaseError):
    def __init__(self, project_slug: str, model_slug: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            title="Toolmodel already exists",
            reason=f"A model with the slug '{model_slug}' already exists in the project '{project_slug}'.",
            err_code="TOOLMODEL_ALREADY_EXISTS",
        )
