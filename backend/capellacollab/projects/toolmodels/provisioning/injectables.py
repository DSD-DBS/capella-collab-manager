# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0
import typing as t

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.users import injectables as users_injectables
from capellacollab.users import models as users_models

from .. import injectables as toolmodels_injectables
from .. import models as toolmodels_models
from . import crud, models


def get_model_provisioning(
    model: t.Annotated[toolmodels_models.DatabaseToolModel, fastapi.Depends(
        toolmodels_injectables.get_existing_capella_model
    )],
    current_user: t.Annotated[users_models.DatabaseUser, fastapi.Depends(
        users_injectables.get_own_user
    )],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
) -> models.DatabaseModelProvisioning | None:
    return crud.get_model_provisioning(db, tool_model=model, user=current_user)
