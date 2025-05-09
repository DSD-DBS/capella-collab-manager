# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import logging

import fastapi

from capellacollab.announcements import routes as announcements_routes
from capellacollab.configuration import routes as configuration_routes
from capellacollab.core.authentication import routes as authentication_routes
from capellacollab.events import routes as events_router
from capellacollab.feedback import routes as feedback_routes
from capellacollab.permissions import routes as permissions_routes
from capellacollab.projects import routes as projects_routes
from capellacollab.sessions import routes as sessions_routes
from capellacollab.settings import routes as settings_routes
from capellacollab.tags import routes as tags_routes
from capellacollab.tools import routes as tools_routes
from capellacollab.users import routes as users_routes

log = logging.getLogger(__name__)


router = fastapi.APIRouter()
router.include_router(
    feedback_routes.router, prefix="/feedback", tags=["Feedback"]
)
router.include_router(
    sessions_routes.router,
    prefix="/sessions",
    tags=["Sessions"],
)
router.include_router(
    projects_routes.router,
    prefix="/projects",
)
router.include_router(
    tools_routes.router,
    prefix="/tools",
    tags=["Tools"],
)
router.include_router(
    users_routes.router,
    prefix="/users",
)
router.include_router(
    permissions_routes.router,
    prefix="/permissions",
    tags=["Permissions"],
)
router.include_router(
    events_router.router,
    prefix="/events",
    tags=["Events"],
)
router.include_router(
    announcements_routes.router,
    prefix="/announcements",
    tags=["Announcements"],
)
router.include_router(
    settings_routes.router,
    prefix="/settings",
)
router.include_router(
    configuration_routes.router,
    prefix="/configurations",
)
router.include_router(
    tags_routes.router,
    prefix="/tags",
)


router.include_router(authentication_routes.router, prefix="/authentication")
