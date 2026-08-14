# 최초 독립 플랜 API 라우터
from fastapi import APIRouter

from app.schemas.schemas import PlanRequest, PlanResponse
from app.services.plan_service import plan_service


router = APIRouter()


@router.post("/api/v1/plan", response_model=PlanResponse)
def create_plan(request: PlanRequest) -> PlanResponse:
    return plan_service.create_plan(request)
