# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from collections import abc

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.users import models as users_models

from . import crud, models

router = fastapi.APIRouter()


@router.get("", response_model=list[models.PolarionInstance])
def list_polarion_instances(
    db: orm.Session = fastapi.Depends(database.get_db),
) -> abc.Sequence[models.DatabasePolarionInstance]:
    return crud.get_polarion_instances(db)


@router.post(
    "",
    response_model=models.PolarionInstance,
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.ADMIN
            )
        )
    ],
)
def create_polarion_instance(
    post_polarion_instance: models.PolarionInstance,
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.DatabasePolarionInstance:
    return crud.create_polarion_instance(db, post_polarion_instance)
