# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import fastapi

from .. import injectables as toolmodels_injectables
from .. import models as toolmodels_models
from . import models


def get_model_restrictions(
    model: toolmodels_models.DatabaseToolModel = fastapi.Depends(
        toolmodels_injectables.get_existing_capella_model
    ),
) -> models.DatabaseToolModelRestrictions | None:
    restrictions = model.restrictions
    assert (
        restrictions
    )  # restrictions are only None for a short time during creation
    return restrictions
