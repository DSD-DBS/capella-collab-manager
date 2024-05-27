# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import importlib
import logging

import fastapi

from capellacollab.core import authentication
from capellacollab.core import responses as auth_responses
from capellacollab.events import routes as events_router
from capellacollab.health import routes as health_routes
from capellacollab.metadata import routes as core_metadata
from capellacollab.notices import routes as notices_routes
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
    responses=auth_responses.api_exceptions(include_authentication=True),
    tags=["Health"],
)
router.include_router(core_metadata.router, tags=["Metadata"])
router.include_router(
    sessions_routes.router,
    prefix="/sessions",
    tags=["Sessions"],
    responses=auth_responses.api_exceptions(include_authentication=True),
)
router.include_router(
    sessions_routes.router_without_authentication,
    prefix="/sessions",
    tags=["Sessions"],
)
router.include_router(
    projects_routes.router,
    prefix="/projects",
    responses=auth_responses.api_exceptions(include_authentication=True),
)
router.include_router(
    tools_routes.router,
    prefix="/tools",
    responses=auth_responses.api_exceptions(include_authentication=True),
    tags=["Tools"],
)
router.include_router(
    users_routes.router,
    prefix="/users",
    responses=auth_responses.api_exceptions(include_authentication=True),
    tags=["Users"],
)
router.include_router(
    events_router.router,
    prefix="/events",
    responses=auth_responses.api_exceptions(include_authentication=True),
    tags=["Events"],
)
router.include_router(
    notices_routes.router, prefix="/notices", tags=["Notices"]
)
router.include_router(
    settings_routes.router,
    prefix="/settings",
    responses=auth_responses.api_exceptions(include_authentication=True),
)
router.include_router(
    settings_routes.router_without_authentication,
    prefix="/settings",
)

# Load authentication routes
ep = authentication.get_authentication_entrypoint()

router.include_router(
    importlib.import_module(".routes", ep.module).router,
    prefix="/authentication",
    tags=[ep.name],
)
