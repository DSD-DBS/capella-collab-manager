# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import importlib
import logging
from importlib import metadata

from fastapi import APIRouter

import capellacollab.config.routes as configuration
import capellacollab.core.metadata as core_metadata
import capellacollab.sessions.routes as sessions
from capellacollab.config import config
from capellacollab.projects import routes as projects
from capellacollab.settings.modelsources.git import routes as git_settings
from capellacollab.settings.modelsources.t4c import routes as t4c_settings
from capellacollab.tools import routes as tools
from capellacollab.utils import git_utils

from ..users import routes
from . import notices

log = logging.getLogger(__name__)


router = APIRouter()
router.include_router(core_metadata.router, tags=["Metadata"])
router.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])
router.include_router(projects.router, prefix="/projects")
router.include_router(tools.router, prefix="/tools")
router.include_router(routes.router, prefix="/users", tags=["Users"])
router.include_router(notices.router, prefix="/notices", tags=["Notices"])
router.include_router(
    configuration.router, prefix="/configurations", tags=["Notices"]
)
router.include_router(
    git_settings.router,
    prefix="/settings/modelsources/git",
    tags=["GitSettings"],
)
router.include_router(
    t4c_settings.router,
    prefix="/settings/modelsources/t4c",
    tags=["GitSettings"],
)
router.include_router(notices.router, prefix="/notices", tags=["Notices"])
router.include_router(
    configuration.router, prefix="/configurations", tags=["Notices"]
)
router.include_router(git_utils.router, prefix="/git-utils")

# Load authentication routes
try:
    ep = next(
        i
        for i in metadata.entry_points()[
            "capellacollab.authentication.providers"
        ]
        if i.name == config["authentication"]["provider"]
    )
except StopIteration:
    raise ValueError(
        "Unknown authentication provider "
        + config["authentication"]["provider"]
    ) from None

router.include_router(
    importlib.import_module(".routes", ep.module).router,
    prefix="/authentication",
    tags=[ep.name],
)
