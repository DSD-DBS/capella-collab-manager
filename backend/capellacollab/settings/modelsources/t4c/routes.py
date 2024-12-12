# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi

from capellacollab.settings.modelsources.t4c.instance import (
    routes as settings_t4c_instance_routes,
)
from capellacollab.settings.modelsources.t4c.license_server import (
    routes as settings_t4c_license_server_routes,
)

router = fastapi.APIRouter()

router.include_router(
    settings_t4c_instance_routes.router,
    prefix="/instances",
    tags=["Settings - Modelsources - T4C - Instances"],
)

router.include_router(
    settings_t4c_license_server_routes.router,
    prefix="/license-servers",
    tags=["Settings - Modelsources - T4C - License Servers"],
)
