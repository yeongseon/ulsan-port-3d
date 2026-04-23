from fastapi import APIRouter

router = APIRouter(tags=["port"])


@router.get("/port/overview")
async def get_port_overview() -> dict:
    return {
        "name": "울산항",
        "zone_count": 0,
        "berth_count": 0,
        "active_vessel_count": 0,
        "alert_count": 0,
        "last_updated": None,
    }


@router.get("/zones")
async def get_zones() -> list:
    return []
