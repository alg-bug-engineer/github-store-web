from fastapi import APIRouter

from app.api.v1.endpoints import auth, repositories, favorites, ai, discover, stats, categories

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(repositories.router, prefix="/repositories", tags=["repositories"])
api_router.include_router(favorites.router, prefix="/favorites", tags=["favorites"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(discover.router, prefix="/discover", tags=["discover"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
