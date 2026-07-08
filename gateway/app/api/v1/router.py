"""
API v1 router — aggregates all v1 endpoint routers.

Import this and include it in the main FastAPI app::

    from app.api.v1.router import api_v1_router
    app.include_router(api_v1_router, prefix="/api/v1")
"""

from fastapi import APIRouter

from app.api.v1.endpoints.chat import router as chat_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.models import router as models_router
from app.api.v1.endpoints.providers import router as providers_router

api_v1_router = APIRouter()

# ── Route registration ────────────────────────────────────────────────────────
api_v1_router.include_router(health_router)
api_v1_router.include_router(chat_router)
api_v1_router.include_router(providers_router)
api_v1_router.include_router(models_router)
