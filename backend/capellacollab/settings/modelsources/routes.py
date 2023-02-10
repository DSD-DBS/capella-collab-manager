# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import APIRouter

from capellacollab.settings.modelsources.git import routes as git_instances
from capellacollab.settings.modelsources.t4c import routes as t4c_settings

router = APIRouter()

router.include_router(
    git_instances.router,
    prefix="/git",
    tags=["Settings - Modelsources - Git"],
)
router.include_router(
    t4c_settings.router,
    prefix="/t4c",
    tags=["Settings - Modelsources - T4C"],
)
