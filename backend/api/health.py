from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from backend.schemas.common import ApiResponse, success_response
from backend.services.health_service import HealthService


router = APIRouter(tags=["health"])


@router.get("/health", response_model=ApiResponse[dict[str, str]])
async def health_check():
    health = HealthService.get_health()

    if health["database"] != "connected":
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "code": status.HTTP_503_SERVICE_UNAVAILABLE,
                "data": health,
                "message": "database unavailable",
            },
        )

    return success_response(health)
