"""
API v1 router aggregator for the Enterprise GenAI Platform.

All v1 endpoint routers are imported and registered here.
The aggregated ``api_router`` is then mounted in ``main.py`` under
the ``/api/v1`` prefix defined in ``Settings.API_V1_PREFIX``.

Adding a new feature module:
    1. Create ``app/api/v1/my_feature.py`` with an APIRouter.
    2. Import the router here.
    3. Call ``api_router.include_router(my_feature.router, prefix="/my-feature")``.
"""

from fastapi import APIRouter

from app.api.v1 import (
    applications,
    auth,
    health,
    organizations,
    teams,
    users,
)

# Root v1 router — all feature routers are nested under this
api_router = APIRouter()

# ---------------------------------------------------------------------------
# Registered routers
# ---------------------------------------------------------------------------
api_router.include_router(health.router)
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(
    organizations.router, prefix="/organizations", tags=["Organization Management"]
)
api_router.include_router(teams.router, prefix="/teams", tags=["Team Management"])
api_router.include_router(users.router, prefix="/users", tags=["User Management"])
api_router.include_router(
    applications.router, prefix="/applications", tags=["Application Management"]
)



# Future routers will be added here as the platform grows, e.g.:
# api_router.include_router(auth.router,        prefix="/auth",        tags=["Authentication"])
# api_router.include_router(providers.router,   prefix="/providers",   tags=["LLM Providers"])
# api_router.include_router(agents.router,      prefix="/agents",      tags=["AI Agents"])
# api_router.include_router(monitoring.router,  prefix="/monitoring",  tags=["Cost Monitoring"])
