# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import status

from capellacollab.core import exceptions as core_exceptions


class PureVariantsIntegrationDisabledError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            err_code="PURE_VARIANTS_INTEGRATION_DISABLED",
            title="pure::variants integration disabled",
            reason=(
                "The tool of this model has no pure::variants integration. "
                "Please enable the pure::variants integration in the settings first."
            ),
        )
