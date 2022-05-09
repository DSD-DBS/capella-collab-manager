# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import importlib
import logging
from importlib import metadata

from fastapi import APIRouter
from t4cclient.config import config
from t4cclient.projects import routes as projects

from . import notices, sessions, users

log = logging.getLogger(__name__)


router = APIRouter()
router.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])
router.include_router(projects.router, prefix="/projects")
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(notices.router, prefix="/notices", tags=["Notices"])

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
