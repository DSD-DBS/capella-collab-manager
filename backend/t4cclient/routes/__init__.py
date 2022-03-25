import logging
from importlib import metadata

from fastapi import APIRouter
from t4cclient import config

from ..core.authentication.provider.azure import routes
from . import notices, repositories, sessions, sync, users

log = logging.getLogger(__name__)

router = APIRouter()
router.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])
router.include_router(sync.router, prefix="/sync", tags=["T4C Server Synchronization"])
router.include_router(repositories.router, prefix="/projects")
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(notices.router, prefix="/notices", tags=["Notices"])

# Load authentication routes
try: 
    ep = next(
        i
        for i in metadata.entry_points()["capellacollab.authentication.providers"]
        if i.name == config.AUTHENTICATION_PROVIDER
    )
    router.include_router(
        ep.load().routes.router,
        prefix="/{project}/extensions/backups/" + ep.name,
        tags=[ep.name],
    )
except StopIteration: 
    raise ValueError(f"Unknown authentication provider {config.AUTHENTICATION_PROVIDER}") from None

router.include_router(ep.load().routes.router, prefix="/authentication", tags=[ep.name])

