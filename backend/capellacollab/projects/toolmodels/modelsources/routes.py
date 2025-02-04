# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi

from capellacollab.projects.toolmodels.modelsources.git import (
    routes as git_routes,
)
from capellacollab.projects.toolmodels.modelsources.t4c import (
    routes as t4c_routes,
)

router = fastapi.APIRouter()

router.include_router(
    git_routes.router,
    prefix="/git",
    tags=["Projects - Models - Git"],
)
router.include_router(
    t4c_routes.router,
    prefix="/t4c",
    tags=["Projects - Models - T4C"],
)
