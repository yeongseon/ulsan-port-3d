from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.common import ProblemDetail
from app.schemas.scenarios import ScenarioFrameResponse, ScenarioSummaryResponse
from app.services import scenarios as scenarios_service

router = APIRouter(tags=["scenarios"])


@router.get(
    "/scenarios",
    response_model=list[ScenarioSummaryResponse],
    responses={500: {"model": ProblemDetail}},
)
async def get_scenarios(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[ScenarioSummaryResponse]:
    return await scenarios_service.get_scenarios(db)


@router.get(
    "/scenarios/{scenario_id}/frames",
    response_model=list[ScenarioFrameResponse],
    responses={404: {"model": ProblemDetail}, 500: {"model": ProblemDetail}},
)
async def get_scenario_frames(
    scenario_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[ScenarioFrameResponse]:
    return await scenarios_service.get_scenario_frames(db, scenario_id=scenario_id)
