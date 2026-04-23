from fastapi import APIRouter

router = APIRouter(tags=["scenarios"])


@router.get("/scenarios")
async def get_scenarios() -> list:
    return []


@router.get("/scenarios/{scenario_id}/frames")
async def get_scenario_frames(scenario_id: str) -> list:
    return []
