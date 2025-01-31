# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import status

from capellacollab.core import exceptions as core_exceptions


class AnnouncementNotFoundError(core_exceptions.BaseError):
    def __init__(self, notice_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            err_code="ANNOUNCEMENT_NOT_FOUND",
            title="Announcement not found",
            reason=f"The announcement with ID {notice_id} doesn't exist",
        )

    @classmethod
    def openapi_example(cls) -> "AnnouncementNotFoundError":
        return cls(-1)
