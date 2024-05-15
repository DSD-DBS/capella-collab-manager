# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import status

from capellacollab.core import exceptions as core_exceptions


class T4CIntegrationNotFoundError(core_exceptions.BaseError):
    def __init__(self, integration_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            err_code="T4C_INTEGRATION_NOT_FOUND",
            title="TeamForCapella project integration not found",
            reason=f"The TeamForCapella project integration with the id {integration_id} doesn't exist in our database.",
        )


class T4CIntegrationDoesntBelongToModel(core_exceptions.BaseError):
    def __init__(self, integration_id: int, model_slug: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            err_code="T4C_INTEGRATION_DOESNT_BELONG_TO_MODEL",
            title="TeamForCapella project integration doesn't belong to requested model",
            reason=f"The TeamForCapella project integration with the id {integration_id} doesn't belong to the model '{model_slug}'.",
        )


class T4CIntegrationAlreadyExists(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            err_code="T4C_INTEGRATION_ALREADY_EXISTS",
            title="TeamForCapella project integration already exists",
            reason="The same TeamForCapella project integration already exists.",
        )


class T4CIntegrationUsedInPipelines(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            title="TeamForCapella project inegration used in pipelines",
            reason=(
                "The TeamForCapella integration is currently used in pipelines. "
                "Please remove the pipeline first."
            ),
            err_code="T4C_INTEGRATION_USED_IN_PIPELINES",
        )
