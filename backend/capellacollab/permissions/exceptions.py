# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import status

from capellacollab.core import exceptions as core_exceptions

from . import models


class InsufficientPermissionError(core_exceptions.BaseError):
    def __init__(
        self,
        required_permission: str,
        required_verbs: set[models.UserTokenVerb],
    ):
        verbs = ", ".join(verb.value for verb in required_verbs)
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            title="Permission denied",
            reason=f"Insufficient permissions: '{required_permission}' permission with verbs {verbs} is required for this transaction.",
            err_code="INSUFFICIENT_PERMISSION",
        )
