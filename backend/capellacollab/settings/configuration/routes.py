# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.users import models as users_models

from . import core, crud, models

router = fastapi.APIRouter(
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.ADMIN
            )
        )
    ],
    tags=["Configuration"],
)

schema_router = fastapi.APIRouter(dependencies=[], tags=["Configuration"])


@router.get(
    f"/{models.GlobalConfiguration._name}",
    response_model=models.GlobalConfiguration,
)
async def get_configuration(
    db: orm.Session = fastapi.Depends(database.get_db),
):
    return core.get_config(db, models.GlobalConfiguration._name)


@router.put(
    f"/{models.GlobalConfiguration._name}",
    response_model=models.GlobalConfiguration,
)
async def update_configuration(
    body: models.GlobalConfiguration,
    db: orm.Session = fastapi.Depends(database.get_db),
):
    configuration = crud.get_configuration_by_name(
        db, models.GlobalConfiguration._name
    )

    if configuration:
        return crud.update_configuration(
            db, configuration, body.model_dump()
        ).configuration
    return crud.create_configuration(
        db,
        name=models.GlobalConfiguration._name,
        configuration=body.model_dump(),
    ).configuration


@schema_router.get(
    f"/{models.GlobalConfiguration._name}/schema", response_model=t.Any
)
async def get_json_schema():
    return models.GlobalConfiguration.model_json_schema()
