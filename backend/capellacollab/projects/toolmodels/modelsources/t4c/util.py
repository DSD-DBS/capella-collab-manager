# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from capellacollab.settings.modelsources.t4c.repositories import (
    models as t4c_repository_models,
)
from capellacollab.tools import models as tools_models

from . import exceptions


def verify_compatibility_of_model_and_server(
    model_name: str,
    model_version: tools_models.DatabaseVersion | None,
    t4c_repository: t4c_repository_models.DatabaseT4CRepository,
):
    server = t4c_repository.instance
    if model_version is None:
        raise exceptions.T4CIntegrationVersionRequired(model_name)

    if (
        t4c_repository.instance.version.id
        not in model_version.config.compatible_versions + [model_version.id]
    ):
        raise exceptions.T4CIntegrationWrongCapellaVersion(
            server.name,
            t4c_repository.name,
            server.version.name,
            server.version.id,
            model_version.name,
            model_version.id,
        )
