# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from . import models


def calculate_project_warnings(
    project: models.DatabaseProject,
) -> list[str]:
    warnings = []

    if not project.models:
        warnings.append("The project has no models. Is it still needed?")

    if not project.description:
        warnings.append("The project has no description.")

    return warnings
