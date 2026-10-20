from datetime import datetime
from time import timezone
from schemas.api import HealthResponse
from fastapi import APIRouter

router = APIRouter(
    prefix="/health",
    tags=["Health"]
)


@router.get("/", response_model=HealthResponse, summary="Basic Health Check Endpoint")
async def health_check() -> HealthResponse:
    return HealthResponse (
        status="ok/healthy",
        timestamp=datetime.now(timezone.utc)
    )