# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.feedback import util as feedback_util
from capellacollab.users import crud as users_crud
from capellacollab.users import models as users_models

from . import core, crud, models, util

router = fastapi.APIRouter(
    tags=["Configuration"],
)

schema_router = fastapi.APIRouter(dependencies=[], tags=["Configuration"])


@router.get(
    "/unified",
)
def get_unified_config(
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.UnifiedConfig:
    cfg = core.get_global_configuration(db)

    return models.UnifiedConfig(
        metadata=util.get_metadata(cfg),
        feedback=util.get_feedback(cfg),
        beta=cfg.beta,
        navbar=cfg.navbar,
    )


@router.get(
    f"/{models.GlobalConfiguration._name}",
    response_model=models.GlobalConfiguration,
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.ADMIN
            )
        )
    ],
)
async def get_configuration(
    db: orm.Session = fastapi.Depends(database.get_db),
):
    return core.get_global_configuration(db)


@router.put(
    f"/{models.GlobalConfiguration._name}",
    response_model=models.GlobalConfiguration,
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.ADMIN
            )
        )
    ],
)
async def update_configuration(
    body: models.GlobalConfiguration,
    db: orm.Session = fastapi.Depends(database.get_db),
):
    configuration = crud.get_configuration_by_name(
        db, models.GlobalConfiguration._name
    )

    feedback_util.validate_global_configuration(body.feedback)

    if body.beta.enabled is False:
        users_crud.unenroll_all_beta_testers(db)

    if body.feedback.enabled is False:
        feedback_util.disable_feedback(body.feedback)

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
