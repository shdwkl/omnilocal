from fastapi import APIRouter

from app.api.routes import items, login, private, users, utils
from app.domains.sync.router import router as sync_router
from app.domains.posts.router import router as posts_router
from app.domains.businesses.router import router as businesses_router
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(sync_router, prefix="/sync", tags=["sync"])
api_router.include_router(posts_router, prefix="/posts", tags=["posts"])
api_router.include_router(businesses_router, prefix="/locations", tags=["businesses"])


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
