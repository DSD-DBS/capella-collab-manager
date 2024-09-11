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


class T4CIntegrationWrongCapellaVersion(core_exceptions.BaseError):
    def __init__(
        self,
        t4c_server_name: str,
        t4c_repository_name: str,
        server_version_name: str,
        server_version_id: int,
        model_version_name: str,
        model_version_id: int,
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            title="The TeamForCapella server is not compatible with Capella model",
            reason=(
                f"The repository '{t4c_repository_name}' of the TeamForCapella server '{t4c_server_name}' "
                f"has version {server_version_name} (ID {server_version_id}), "
                f"but the model has version {model_version_name} (ID {model_version_id}). "
                "Make sure that those versions match or are compatible with each other."
            ),
            err_code="T4C_INTEGRATION_WRONG_CAPELLA_VERSION",
        )


class T4CIntegrationVersionRequired(core_exceptions.BaseError):
    def __init__(self, toolmodel_slug: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            title="The Capella model requires a version to proceed",
            reason=(
                f"To link a TeamForCapella repository, the Capella model '{toolmodel_slug}' has to have a version. "
                "Please add a version first."
            ),
            err_code="T4C_INTEGRATION_NO_VERSION",
        )
