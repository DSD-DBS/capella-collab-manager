# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from . import models


def calculate_model_warnings(
    model: models.DatabaseToolModel,
) -> list[str]:
    warnings = []
    if not model.nature:
        warnings.append(
            "The nature is not set for this model. Without a nature, some features may not work as expected"
        )
    if not model.version:
        warnings.append(
            "The tool version is not set for this model. Without a set tool version, the model only has a limited range of features"
        )
    if not model.description:
        warnings.append("The model has no description.")
    return warnings
