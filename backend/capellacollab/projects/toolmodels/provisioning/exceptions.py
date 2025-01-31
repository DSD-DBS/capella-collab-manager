# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import status

from capellacollab.core import exceptions as core_exceptions


class ProvisioningNotFoundError(core_exceptions.BaseError):
    def __init__(self, project_slug: str, model_slug: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            title="Provisioning not found",
            reason=f"Couldn't find a provisioning for the model '{model_slug}' in the project '{project_slug}'.",
            err_code="PROVISIONING_NOT_FOUND",
        )

    @classmethod
    def openapi_example(cls) -> "ProvisioningNotFoundError":
        return cls("coffee-machine", "coffee-machine")
