from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.static import Berth, Operator, PortZone
from app.models.timeseries import LatestBerthStatus
from app.schemas.berth import BerthResponse, BerthStatusResponse
from app.services.common import not_found, parse_uuid_or_none, stringify_id, to_utc_iso


def _berth_select():
    return (
        select(
            Berth,
            PortZone,
            Operator,
            LatestBerthStatus,
            func.ST_Y(Berth.geometry),
            func.ST_X(Berth.geometry),
        )
        .join(PortZone, PortZone.zone_id == Berth.zone_id)
        .outerjoin(Operator, Operator.operator_id == Berth.operator_id)
        .outerjoin(
            LatestBerthStatus,
            LatestBerthStatus.berth_facility_code == Berth.facility_code,
        )
    )


def _map_berth(
    berth: Berth,
    zone_model: PortZone,
    operator_model: Operator | None,
    status_model: LatestBerthStatus | None,
    latitude: float | None,
    longitude: float | None,
) -> BerthResponse:
    return BerthResponse(
        berth_id=stringify_id(berth.berth_id),
        facility_code=berth.facility_code,
        name=berth.name,
        zone_id=stringify_id(zone_model.zone_id),
        zone_name=zone_model.name,
        operator_id=stringify_id(operator_model.operator_id)
        if operator_model is not None
        else None,
        operator_name=operator_model.name if operator_model is not None else None,
        length=berth.length,
        depth=berth.depth,
        latitude=latitude,
        longitude=longitude,
        latest_status=status_model.status if status_model is not None else None,
        latest_status_detail=status_model.status_detail if status_model is not None else None,
        latest_status_updated_at=to_utc_iso(status_model.updated_at)
        if status_model is not None
        else None,
        created_at=to_utc_iso(berth.created_at),
    )


async def get_berths(
    db: AsyncSession, *, zone: str | None, status: str | None, operator: str | None
) -> list[BerthResponse]:
    stmt = _berth_select().order_by(PortZone.name.asc(), Berth.name.asc())
    if zone:
        stmt = stmt.where(PortZone.name == zone)
    if status:
        stmt = stmt.where(LatestBerthStatus.status == status)
    if operator:
        stmt = stmt.where(Operator.name == operator)
    rows = (await db.execute(stmt)).all()
    return [
        _map_berth(berth, zone_model, operator_model, status_model, latitude, longitude)
        for berth, zone_model, operator_model, status_model, latitude, longitude in rows
    ]


async def get_berth_detail(db: AsyncSession, berth_id: str) -> BerthResponse:
    berth_uuid = parse_uuid_or_none(berth_id)
    stmt = _berth_select().where(Berth.facility_code == berth_id)
    if berth_uuid is not None:
        stmt = _berth_select().where(
            (Berth.facility_code == berth_id) | (Berth.berth_id == berth_uuid)
        )
    row = (await db.execute(stmt)).first()
    if row is None:
        raise not_found(f"Berth '{berth_id}' was not found.")

    berth, zone_model, operator_model, status_model, latitude, longitude = row
    return _map_berth(berth, zone_model, operator_model, status_model, latitude, longitude)


async def get_live_berth_status(db: AsyncSession) -> list[BerthStatusResponse]:
    stmt = select(LatestBerthStatus).order_by(
        LatestBerthStatus.zone_name.asc(), LatestBerthStatus.berth_name.asc()
    )
    statuses = (await db.scalars(stmt)).all()
    return [
        BerthStatusResponse(
            berth_facility_code=status.berth_facility_code,
            berth_name=status.berth_name,
            zone_name=status.zone_name,
            status=status.status,
            status_detail=status.status_detail,
            updated_at=to_utc_iso(status.updated_at),
        )
        for status in statuses
    ]
