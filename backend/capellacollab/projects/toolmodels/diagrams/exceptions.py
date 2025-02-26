# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import status

from capellacollab.core import exceptions as core_exceptions


class DiagramCacheNotConfiguredProperlyError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            title="Diagram cache not configured properly",
            reason=(
                "The diagram cache is not configured properly. "
                "Please contact your diagram cache administrator."
            ),
            err_code="DIAGRAM_CACHE_NOT_CONFIGURED_PROPERLY",
        )

    @classmethod
    def openapi_example(cls) -> "DiagramCacheNotConfiguredProperlyError":
        return cls()


class FileExtensionNotSupportedError(core_exceptions.BaseError):
    def __init__(self, fileextension: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            title="File extension not supported",
            reason=f"The file extension {fileextension} is not supported.",
            err_code="FILE_EXTENSION_NOT_SUPPORTED",
        )

    @classmethod
    def openapi_example(cls) -> "FileExtensionNotSupportedError":
        return cls("png")


class DiagramNotFoundError(core_exceptions.BaseError):
    def __init__(self, diagram_uuid: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            title="Couldn't find the requested diagram",
            reason=(
                f"The diagram with the UUID '{diagram_uuid}' could not be found in the diagram cache index."
            ),
            err_code="DIAGRAM_CACHE_DIAGRAM_NOT_FOUND",
        )

    @classmethod
    def openapi_example(cls) -> "DiagramNotFoundError":
        return cls("_yYhrh3jqEea__MYrXGSERA")


class DiagramNotSuccessfulError(core_exceptions.BaseError):
    def __init__(self, diagram_uuid: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            title="The requested diagram export was not successful",
            reason=(
                f"The diagram with the UUID '{diagram_uuid}' has been marked"
                " as unsuccessful in the diagram cache index."
            ),
            err_code="DIAGRAM_CACHE_DIAGRAM_NOT_SUCCESSFUL",
        )

    @classmethod
    def openapi_example(cls) -> "DiagramNotSuccessfulError":
        return cls("_yYhrh3jqEea__MYrXGSERA")
