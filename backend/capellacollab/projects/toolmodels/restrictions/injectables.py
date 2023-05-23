# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import fastapi

from .. import injectables as toolmodels_injectables
from .. import models as toolmodels_models
from . import models


def get_model_restrictions(
    model: toolmodels_models.DatabaseCapellaModel = fastapi.Depends(
        toolmodels_injectables.get_existing_capella_model
    ),
) -> models.DatabaseToolModelRestrictions:
    return model.restrictions
