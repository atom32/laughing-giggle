"""
Main API router for Park Tycoon Game
"""
from fastapi import APIRouter

# Import route modules
from app.api.auth import router as auth_router
from app.api.i18n import router as i18n_router
# from app.api.player import router as player_router
# from app.api.livestock import router as livestock_router
# from app.api.modules import router as modules_router

api_router = APIRouter()

# Health check endpoint
@api_router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Park Tycoon Game API is running"}

# Include route modules
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(i18n_router)  # i18n router already has /i18n prefix
# api_router.include_router(player_router, prefix="/players", tags=["players"])
# api_router.include_router(livestock_router, prefix="/livestock", tags=["livestock"])
# api_router.include_router(modules_router, prefix="/modules", tags=["modules"])