from fastapi import APIRouter

from . import notices, oauth, repositories, sessions, sync, users

router = APIRouter()
router.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])
router.include_router(sync.router, prefix="/sync", tags=["T4C Server Synchronization"])
router.include_router(repositories.router, prefix="/projects")
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(oauth.router, prefix="/auth/oauth", tags=["Authentication"])
router.include_router(notices.router, prefix="/notices", tags=["Notices"])
