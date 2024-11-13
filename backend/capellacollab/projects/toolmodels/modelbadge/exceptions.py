# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import status

from capellacollab.core import exceptions as core_exceptions


class ModelBadgeNotConfiguredProperlyError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            title="Model complexity badge not configured properly",
            reason=(
                "The model complexity badge is not configured properly. "
                "Please contact your project admin or system administrator."
            ),
            err_code="MODEL_COMPLEXITY_BADGE_NOT_CONFIGURED_PROPERLY",
        )
