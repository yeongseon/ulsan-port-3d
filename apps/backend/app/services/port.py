from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.documents import Alert
from app.models.static import Berth, Buoy, PortZone
from app.models.timeseries import LatestVesselPosition
from app.schemas.port import PortOverviewResponse, ZoneResponse
from app.services.common import stringify_id, to_utc_iso


async def get_port_overview(db: AsyncSession) -> PortOverviewResponse:
    zone_count = await db.scalar(select(func.count()).select_from(PortZone))
    berth_count = await db.scalar(select(func.count()).select_from(Berth))
    active_vessel_count = await db.scalar(select(func.count()).select_from(LatestVesselPosition))
    alert_count = await db.scalar(
        select(func.count()).select_from(Alert).where(Alert.is_active.is_(True))
    )

    latest_values = [
        await db.scalar(select(func.max(PortZone.created_at))),
        await db.scalar(select(func.max(LatestVesselPosition.updated_at))),
        await db.scalar(select(func.max(Alert.created_at))),
    ]
    last_updated = max((value for value in latest_values if value is not None), default=None)

    return PortOverviewResponse(
        name="울산항",
        zone_count=zone_count or 0,
        berth_count=berth_count or 0,
        active_vessel_count=active_vessel_count or 0,
        alert_count=alert_count or 0,
        last_updated=to_utc_iso(last_updated),
    )


async def get_zones(db: AsyncSession) -> list[ZoneResponse]:
    berth_counts = (
        select(Berth.zone_id.label("zone_id"), func.count(Berth.berth_id).label("berth_count"))
        .group_by(Berth.zone_id)
        .subquery()
    )
    buoy_counts = (
        select(Buoy.zone_id.label("zone_id"), func.count(Buoy.buoy_id).label("buoy_count"))
        .group_by(Buoy.zone_id)
        .subquery()
    )
    stmt: Select[tuple[PortZone, int | None, int | None]] = (
        select(PortZone, berth_counts.c.berth_count, buoy_counts.c.buoy_count)
        .outerjoin(berth_counts, berth_counts.c.zone_id == PortZone.zone_id)
        .outerjoin(buoy_counts, buoy_counts.c.zone_id == PortZone.zone_id)
        .order_by(PortZone.name.asc())
    )
    result = await db.execute(stmt)
    return [
        ZoneResponse(
            zone_id=stringify_id(zone.zone_id),
            name=zone.name,
            zone_type=zone.zone_type,
            description=zone.description,
            berth_count=berth_count or 0,
            buoy_count=buoy_count or 0,
            created_at=to_utc_iso(zone.created_at),
        )
        for zone, berth_count, buoy_count in result.all()
    ]
