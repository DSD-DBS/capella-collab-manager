# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi

from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.settings.integrations.purevariants import (
    routes as purevariants_routes,
)
from capellacollab.settings.modelsources import routes as modelsources_routes
from capellacollab.users import models as users_models

router = fastapi.APIRouter(
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.USER
            )
        )
    ]
)
router.include_router(
    modelsources_routes.router,
    prefix="/modelsources",
)
router.include_router(
    purevariants_routes.router, prefix="/integrations/pure-variants"
)
