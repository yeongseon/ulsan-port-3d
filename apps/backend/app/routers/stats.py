from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.common import ProblemDetail
from app.schemas.stats import (
    ArrivalStatResponse,
    CongestionStatResponse,
    LiquidCargoStatResponse,
)
from app.services import stats as stats_service

router = APIRouter(tags=["stats"])


@router.get(
    "/stats/arrivals",
    response_model=list[ArrivalStatResponse],
    responses={500: {"model": ProblemDetail}},
)
async def get_arrival_stats(
    from_date: str | None = None,
    to_date: str | None = None,
    zone: str | None = None,
    *,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[ArrivalStatResponse]:
    return await stats_service.get_arrival_stats(
        db, from_date=from_date, to_date=to_date, zone=zone
    )


@router.get(
    "/stats/liquid-cargo",
    response_model=list[LiquidCargoStatResponse],
    responses={500: {"model": ProblemDetail}},
)
async def get_liquid_cargo_stats(
    from_date: str | None = None,
    to_date: str | None = None,
    zone: str | None = None,
    *,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[LiquidCargoStatResponse]:
    return await stats_service.get_liquid_cargo_stats(
        db, from_date=from_date, to_date=to_date, zone=zone
    )


@router.get(
    "/stats/congestion",
    response_model=list[CongestionStatResponse],
    responses={500: {"model": ProblemDetail}},
)
async def get_congestion_stats(
    from_date: str | None = None,
    to_date: str | None = None,
    *,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[CongestionStatResponse]:
    return await stats_service.get_congestion_stats(db, from_date=from_date, to_date=to_date)
