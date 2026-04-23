from fastapi import APIRouter

router = APIRouter(tags=["stats"])


@router.get("/stats/arrivals")
async def get_arrival_stats(
    from_date: str | None = None,
    to_date: str | None = None,
    zone: str | None = None,
) -> list:
    return []


@router.get("/stats/liquid-cargo")
async def get_liquid_cargo_stats(
    from_date: str | None = None,
    to_date: str | None = None,
    zone: str | None = None,
) -> list:
    return []


@router.get("/stats/congestion")
async def get_congestion_stats(
    from_date: str | None = None,
    to_date: str | None = None,
) -> list:
    return []
