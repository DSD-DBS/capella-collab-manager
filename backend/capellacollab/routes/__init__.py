# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

# Standard library:
import importlib
import logging
from importlib import metadata

# 3rd party:
from fastapi import APIRouter

# 1st party:
import capellacollab.config.routes as configuration
from capellacollab.config import config
from capellacollab.projects import routes as projects
from capellacollab.settings.modelsources.git import routes as git_settings

# local:
from . import notices, sessions, users

log = logging.getLogger(__name__)


router = APIRouter()
router.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])
router.include_router(projects.router, prefix="/projects")
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(notices.router, prefix="/notices", tags=["Notices"])
router.include_router(configuration.router, prefix="/configurations", tags=["Notices"])
router.include_router(
    git_settings.router, prefix="/settings/modelsources/git", tags=["GitSettings"]
)

# Load authentication routes
try:
    ep = next(
        i
        for i in metadata.entry_points()["capellacollab.authentication.providers"]
        if i.name == config["authentication"]["provider"]
    )
except StopIteration:
    raise ValueError(
        f"Unknown authentication provider " + config["authentication"]["provider"]
    ) from None

router.include_router(
    importlib.import_module(".routes", ep.module).router,
    prefix="/authentication",
    tags=[ep.name],
)
