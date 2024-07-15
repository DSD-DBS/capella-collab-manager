# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import status

from capellacollab.core import exceptions as core_exceptions


class WorkspaceNotFound(core_exceptions.BaseError):
    def __init__(self, username: str, workspace_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            title="Workspace not found",
            reason=f"The workspace with ID {workspace_id} doesn't exist for user '{username}'.",
            err_code="USER_WORKSPACE_NOT_FOUND",
        )
