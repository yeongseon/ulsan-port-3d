from fastapi import APIRouter

router = APIRouter(tags=["vessels"])


@router.get("/vessels/live")
async def get_vessels_live(zone: str | None = None, ship_type: str | None = None) -> list:
    return []


@router.get("/vessels/{vessel_id}")
async def get_vessel_detail(vessel_id: str) -> dict:
    return {"vessel_id": vessel_id, "detail": "not implemented"}
