# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.settings.configuration import core as config_core
from capellacollab.settings.configuration import models as config_models

router = fastapi.APIRouter()


@router.get(
    "/navbar",
    response_model=config_models.NavbarConfiguration,
)
def get_navbar(db: orm.Session = fastapi.Depends(database.get_db)):
    cfg = config_core.get_global_configuration(db)

    return config_models.NavbarConfiguration.model_validate(
        cfg.navbar.model_dump()
    )
