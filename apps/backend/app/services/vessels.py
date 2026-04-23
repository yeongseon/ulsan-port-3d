from sqlalchemy import Select, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.static import Berth, PortZone
from app.models.timeseries import LatestVesselPosition, VesselEvent
from app.schemas.vessel import VesselDetailResponse, VesselEventResponse, VesselLiveResponse
from app.services.common import not_found, to_utc_iso


def _map_live_position(position: LatestVesselPosition) -> VesselLiveResponse:
    return VesselLiveResponse(
        vessel_id=position.vessel_id,
        name=position.name,
        call_sign=position.call_sign,
        imo=position.imo,
        ship_type=position.ship_type,
        gross_tonnage=position.gross_tonnage,
        lat=position.lat,
        lon=position.lon,
        speed=position.speed,
        course=position.course,
        heading=position.heading,
        draft=position.draft,
        observed_at=to_utc_iso(position.observed_at) or "",
        updated_at=to_utc_iso(position.updated_at),
    )


def _map_event(event: VesselEvent) -> VesselEventResponse:
    return VesselEventResponse(
        event_id=str(event.event_id),
        vessel_id=event.vessel_id,
        call_sign=event.call_sign,
        event_type=event.event_type,
        berth_facility_code=event.berth_facility_code,
        event_time=to_utc_iso(event.event_time) or "",
        detail=event.detail,
        raw_data=event.raw_data,
        created_at=to_utc_iso(event.created_at),
    )


async def get_live_vessels(
    db: AsyncSession, *, zone: str | None, ship_type: str | None
) -> list[VesselLiveResponse]:
    stmt: Select[tuple[LatestVesselPosition]] = select(LatestVesselPosition)
    if ship_type:
        stmt = stmt.where(LatestVesselPosition.ship_type == ship_type)
    if zone:
        zone_filtered_vessels = (
            select(VesselEvent.vessel_id)
            .join(Berth, Berth.facility_code == VesselEvent.berth_facility_code)
            .join(PortZone, PortZone.zone_id == Berth.zone_id)
            .where(PortZone.name == zone)
            .distinct()
            .subquery()
        )
        stmt = stmt.join(
            zone_filtered_vessels,
            zone_filtered_vessels.c.vessel_id == LatestVesselPosition.vessel_id,
        )
    stmt = stmt.order_by(LatestVesselPosition.observed_at.desc())
    result = await db.scalars(stmt)
    return [_map_live_position(position) for position in result.all()]


async def get_vessel_detail(db: AsyncSession, vessel_id: str) -> VesselDetailResponse:
    position = await db.get(LatestVesselPosition, vessel_id)
    if position is None:
        raise not_found(f"Vessel '{vessel_id}' was not found.")

    events_stmt = (
        select(VesselEvent)
        .where(VesselEvent.vessel_id == vessel_id)
        .order_by(desc(VesselEvent.event_time))
        .limit(20)
    )
    events = (await db.scalars(events_stmt)).all()
    return VesselDetailResponse(
        vessel_id=vessel_id,
        latest_position=_map_live_position(position),
        events=[_map_event(event) for event in events],
    )
