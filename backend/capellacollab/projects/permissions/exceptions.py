# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import status

from capellacollab.core import exceptions as core_exceptions
from capellacollab.permissions import models as permissions_models


class InsufficientProjectPermissionError(core_exceptions.BaseError):
    def __init__(
        self,
        required_permission: str,
        required_verbs: set[permissions_models.UserTokenVerb],
        project_name: str,
    ):
        verbs = ", ".join(verb.value for verb in required_verbs)
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            title="Permission denied",
            reason=(
                f"Insufficient permissions: '{required_permission}' permission with verb(s) {verbs}"
                f" in the project '{project_name}' is required for this transaction."
            ),
            err_code="INSUFFICIENT_PROJECT_PERMISSION",
        )

    @classmethod
    def openapi_example(cls) -> "InsufficientProjectPermissionError":
        return cls(
            "permission",
            {permissions_models.UserTokenVerb.GET},
            "In-Flight Entertainment",
        )
