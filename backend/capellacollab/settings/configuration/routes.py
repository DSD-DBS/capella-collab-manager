# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.users import models as users_models

from . import crud, models

router = fastapi.APIRouter(
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.ADMIN
            )
        )
    ]
)


@router.get("/global", response_model=models.GlobalConfiguration)
def get_global_configuration(
    db: orm.Session = fastapi.Depends(database.get_db),
):
    configuration = crud.get_configuration_by_name(db, "global")
    if configuration:
        return configuration.configuration
    return models.GlobalConfiguration().model_validate({})


@router.put("/global", response_model=models.GlobalConfiguration)
def update_global_configuration(
    body: models.GlobalConfiguration,
    db: orm.Session = fastapi.Depends(database.get_db),
):
    configuration = crud.get_configuration_by_name(db, "global")

    if configuration:
        return crud.update_configuration(db, configuration, body.model_dump())
    return crud.create_configuration(
        db, name="global", configuration=body.model_dump()
    )
