# 플랜 재계획 API 라우터
from fastapi import APIRouter

from app.schemas.schemas import ReplanRequest, ReplanResponse
from app.services.plan_service import plan_service


router = APIRouter()


@router.post("/api/v1/replan", response_model=ReplanResponse)
def replan(request: ReplanRequest) -> ReplanResponse:
    return plan_service.replan(request)
