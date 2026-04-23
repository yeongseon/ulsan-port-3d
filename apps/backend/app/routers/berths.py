from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.berth import BerthResponse, BerthStatusResponse
from app.schemas.common import ProblemDetail
from app.services import berths as berth_service

router = APIRouter(tags=["berths"])


@router.get(
    "/berths",
    response_model=list[BerthResponse],
    responses={500: {"model": ProblemDetail}},
)
async def get_berths(
    zone: str | None = None,
    status: str | None = None,
    operator: str | None = None,
    *,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[BerthResponse]:
    return await berth_service.get_berths(db, zone=zone, status=status, operator=operator)


@router.get(
    "/berth-status/live",
    response_model=list[BerthStatusResponse],
    responses={500: {"model": ProblemDetail}},
)
async def get_berth_status_live(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[BerthStatusResponse]:
    return await berth_service.get_live_berth_status(db)
