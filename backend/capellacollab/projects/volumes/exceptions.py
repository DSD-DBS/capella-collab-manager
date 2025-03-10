# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import status

from capellacollab.core import exceptions


class OnlyOneVolumePerProjectError(exceptions.BaseError):
    def __init__(self, project_slug: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            title="Only one volume per project allowed",
            reason=(
                f"You can't add another volume to the project '{project_slug}'."
                " Each project can only have a maximum of one volume."
                " Reuse the existing volume or delete the old volume first."
            ),
            err_code="ONLY_ONE_VOLUME_PER_PROJECT",
        )

    @classmethod
    def openapi_example(cls) -> "OnlyOneVolumePerProjectError":
        return cls("test")


class VolumeNotFoundError(exceptions.BaseError):
    def __init__(self, volume_id: int, project_slug: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            title="Project volume not found",
            reason=(
                f"Couldn't find the volume {volume_id} in the project '{project_slug}'."
            ),
            err_code="PROJECT_VOLUME_NOT_FOUND",
        )

    @classmethod
    def openapi_example(cls) -> "VolumeNotFoundError":
        return cls(-1, "test")
