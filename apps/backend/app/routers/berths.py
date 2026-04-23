from fastapi import APIRouter

router = APIRouter(tags=["berths"])


@router.get("/berths")
async def get_berths(
    zone: str | None = None,
    status: str | None = None,
    operator: str | None = None,
) -> list:
    return []


@router.get("/berth-status/live")
async def get_berth_status_live() -> list:
    return []
