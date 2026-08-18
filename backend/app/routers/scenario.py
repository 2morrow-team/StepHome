from fastapi import APIRouter

from app.schemas.schemas import ScenarioRequest, ScenarioResponse
from app.services.scenario_service import scenario_service


router = APIRouter()


@router.post(
    "/api/v1/scenarios",
    response_model=ScenarioResponse,
    response_model_exclude_none=True,
)
def compare_scenarios(request: ScenarioRequest) -> ScenarioResponse:
    return scenario_service.compare(request)
