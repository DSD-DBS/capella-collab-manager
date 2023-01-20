# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import importlib
import logging

from fastapi import APIRouter

import capellacollab.core.metadata as core_metadata
import capellacollab.notices.routes as notices
import capellacollab.sessions.routes as sessions
import capellacollab.settings.routes as settings
import capellacollab.users.routes as users
from capellacollab.core.authentication import get_authentication_entrypoint
from capellacollab.core.authentication.responses import (
    AUTHENTICATION_RESPONSES,
)
from capellacollab.projects import routes as projects
from capellacollab.tools import routes as tools

log = logging.getLogger(__name__)


router = APIRouter()
router.include_router(core_metadata.router, tags=["Metadata"])
router.include_router(
    sessions.router,
    prefix="/sessions",
    tags=["Sessions"],
    responses=AUTHENTICATION_RESPONSES,
)
router.include_router(
    projects.router,
    prefix="/projects",
    responses=AUTHENTICATION_RESPONSES,
)
router.include_router(
    tools.router,
    prefix="/tools",
    responses=AUTHENTICATION_RESPONSES,
    tags=["Tools"],
)
router.include_router(
    users.router,
    prefix="/users",
    responses=AUTHENTICATION_RESPONSES,
    tags=["Users"],
)
router.include_router(notices.router, prefix="/notices", tags=["Notices"])
router.include_router(
    settings.router,
    prefix="/settings",
    responses=AUTHENTICATION_RESPONSES,
)

# Load authentication routes
ep = get_authentication_entrypoint()

router.include_router(
    importlib.import_module(".routes", ep.module).router,
    prefix="/authentication",
    tags=[ep.name],
)
