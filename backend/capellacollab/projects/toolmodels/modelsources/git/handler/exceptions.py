# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import status

from capellacollab.core import exceptions as core_exceptions


class GitInstanceUnsupportedError(core_exceptions.BaseError):
    def __init__(self, instance_name: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            title="Git instance unsupported",
            reason=f"The Git instance '{instance_name}' doesn't support the requested operation.",
            err_code="GIT_INSTANCE_UNSUPPORTED",
        )


class NoMatchingGitInstanceError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            title="No matching git instance",
            reason=(
                "No matching git instance was found for the primary git model. "
                "Please contact your administrator."
            ),
            err_code="NO_MATCHING_GIT_INSTANCE",
        )


class GitInstanceAPIEndpointNotFoundError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            title="Git instance API endpoint not found",
            reason=(
                "The used Git instance has no API endpoint defined. "
                "Please contact your administrator."
            ),
            err_code="GIT_INSTANCE_NO_API_ENDPOINT_DEFINED",
        )
