from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.timeseries import ArrivalStatMonthly, CargoStatMonthly, CongestionStat
from app.schemas.stats import (
    ArrivalStatResponse,
    CongestionStatResponse,
    LiquidCargoStatResponse,
)
from app.services.common import to_utc_iso


async def get_arrival_stats(
    db: AsyncSession, *, from_date: str | None, to_date: str | None, zone: str | None
) -> list[ArrivalStatResponse]:
    stmt = select(ArrivalStatMonthly)
    if from_date:
        stmt = stmt.where(ArrivalStatMonthly.year_month >= from_date)
    if to_date:
        stmt = stmt.where(ArrivalStatMonthly.year_month <= to_date)
    if zone:
        stmt = stmt.where(ArrivalStatMonthly.zone_name == zone)
    stmt = stmt.order_by(ArrivalStatMonthly.year_month.desc(), ArrivalStatMonthly.berth_name.asc())
    items = (await db.scalars(stmt)).all()
    return [
        ArrivalStatResponse(
            year_month=item.year_month,
            zone_name=item.zone_name,
            berth_name=item.berth_name,
            vessel_count=item.vessel_count,
            created_at=to_utc_iso(item.created_at),
        )
        for item in items
    ]


async def get_liquid_cargo_stats(
    db: AsyncSession, *, from_date: str | None, to_date: str | None, zone: str | None
) -> list[LiquidCargoStatResponse]:
    stmt = select(CargoStatMonthly)
    if from_date:
        stmt = stmt.where(CargoStatMonthly.year_month >= from_date)
    if to_date:
        stmt = stmt.where(CargoStatMonthly.year_month <= to_date)
    if zone:
        stmt = stmt.where(CargoStatMonthly.zone_name == zone)
    stmt = stmt.order_by(CargoStatMonthly.year_month.desc(), CargoStatMonthly.berth_name.asc())
    items = (await db.scalars(stmt)).all()
    return [
        LiquidCargoStatResponse(
            year_month=item.year_month,
            zone_name=item.zone_name,
            berth_name=item.berth_name,
            cargo_type=item.cargo_type,
            volume_ton=item.volume_ton,
            created_at=to_utc_iso(item.created_at),
        )
        for item in items
    ]


async def get_congestion_stats(
    db: AsyncSession, *, from_date: str | None, to_date: str | None
) -> list[CongestionStatResponse]:
    stmt = select(CongestionStat)
    if from_date:
        stmt = stmt.where(CongestionStat.stat_date >= from_date)
    if to_date:
        stmt = stmt.where(CongestionStat.stat_date <= to_date)
    stmt = stmt.order_by(CongestionStat.stat_date.desc())
    items = (await db.scalars(stmt)).all()
    return [
        CongestionStatResponse(
            stat_date=item.stat_date,
            waiting_count=item.waiting_count,
            avg_wait_hours=item.avg_wait_hours,
            created_at=to_utc_iso(item.created_at),
        )
        for item in items
    ]
