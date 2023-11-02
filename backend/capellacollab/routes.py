# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import importlib
import logging

import fastapi

from capellacollab.core import authentication
from capellacollab.core import metadata as core_metadata
from capellacollab.core.authentication import responses as auth_responses
from capellacollab.health import routes as health_routes
from capellacollab.notices import routes as notices_routes
from capellacollab.plugins import routes as plugins_routes
from capellacollab.projects import routes as projects_routes
from capellacollab.sessions import routes as sessions_routes
from capellacollab.settings import routes as settings_routes
from capellacollab.tools import routes as tools_routes
from capellacollab.users import routes as users_routes

log = logging.getLogger(__name__)


router = fastapi.APIRouter()
router.include_router(
    health_routes.router,
    prefix="/health",
    responses=auth_responses.AUTHENTICATION_RESPONSES,
    tags=["Health"],
)
router.include_router(core_metadata.router, tags=["Metadata"])
router.include_router(
    sessions_routes.router,
    prefix="/sessions",
    tags=["Sessions"],
    responses=auth_responses.AUTHENTICATION_RESPONSES,
)
router.include_router(
    projects_routes.router,
    prefix="/projects",
    responses=auth_responses.AUTHENTICATION_RESPONSES,
)
router.include_router(
    plugins_routes.router,
    tags=["Plugins"],
    prefix="/plugins",
    responses=auth_responses.AUTHENTICATION_RESPONSES,
)
router.include_router(
    plugins_routes.schema_router,
    tags=["Plugins"],
    prefix="/plugins-schema",
    responses=auth_responses.AUTHENTICATION_RESPONSES,
)
router.include_router(
    tools_routes.router,
    prefix="/tools",
    responses=auth_responses.AUTHENTICATION_RESPONSES,
    tags=["Tools"],
)
router.include_router(
    users_routes.router,
    prefix="/users",
    responses=auth_responses.AUTHENTICATION_RESPONSES,
    tags=["Users"],
)
router.include_router(
    notices_routes.router, prefix="/notices", tags=["Notices"]
)
router.include_router(
    settings_routes.router,
    prefix="/settings",
    responses=auth_responses.AUTHENTICATION_RESPONSES,
)

# Load authentication routes
ep = authentication.get_authentication_entrypoint()

router.include_router(
    importlib.import_module(".routes", ep.module).router,
    prefix="/authentication",
    tags=["Authentication"],
)
