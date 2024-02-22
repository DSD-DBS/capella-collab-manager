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
