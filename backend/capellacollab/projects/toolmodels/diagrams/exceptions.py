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


class FileExtensionNotSupportedError(core_exceptions.BaseError):
    def __init__(self, fileextension: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            title="File extension not supported",
            reason=f"The file extension {fileextension} is not supported.",
            err_code="FILE_EXTENSION_NOT_SUPPORTED",
        )
