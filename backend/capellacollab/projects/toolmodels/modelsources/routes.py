# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from fastapi import APIRouter, Depends

from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.projects.users.models import ProjectUserRole

from .git.routes import router as router_sources_git
from .t4c.routes import router as router_sources_t4c

router = APIRouter(
    dependencies=[
        Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=ProjectUserRole.USER
            )
        )
    ],
)

router.include_router(
    router_sources_git,
    prefix="/git",
    tags=["Projects - Models - Git"],
)
router.include_router(
    router_sources_t4c,
    prefix="/t4c",
    tags=["Projects - Models - T4C"],
)
