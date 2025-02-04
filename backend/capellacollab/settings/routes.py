# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi

from capellacollab.settings.integrations.purevariants import (
    routes as purevariants_routes,
)
from capellacollab.settings.modelsources import routes as modelsources_routes

router = fastapi.APIRouter()

router.include_router(
    modelsources_routes.router,
    prefix="/modelsources",
)
router.include_router(
    purevariants_routes.router, prefix="/integrations/pure-variants"
)
