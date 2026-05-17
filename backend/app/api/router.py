from fastapi import APIRouter

from app.api.endpoints.health import router as health_router
from app.api.endpoints.apis import router as apis_router
from app.api.endpoints.scoring import router as scoring_router
from app.api.endpoints.dependencies import router as dependencies_router
from app.api.endpoints.simulator import router as simulator_router
from app.api.endpoints.alerts import router as alerts_router
from app.api.endpoints.analytics import router as analytics_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(apis_router, tags=["apis"])
api_router.include_router(scoring_router, tags=["scoring"])
api_router.include_router(dependencies_router, tags=["dependencies"])
api_router.include_router(simulator_router, tags=["simulator"])
api_router.include_router(alerts_router, tags=["alerts"])
api_router.include_router(analytics_router, tags=["analytics"])

