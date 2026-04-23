from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.static import Buoy, CargoType, PortZone


DEFAULT_ZONES = [
    {"name": "북항", "zone_type": "harbor", "description": "North Harbor zone"},
    {"name": "남항", "zone_type": "harbor", "description": "South Harbor zone"},
    {"name": "오일터미널", "zone_type": "terminal", "description": "Oil terminal zone"},
    {"name": "컨테이너부두", "zone_type": "terminal", "description": "Container terminal zone"},
    {
        "name": "석유화학단지",
        "zone_type": "industrial",
        "description": "Petrochemical complex zone",
    },
]

DEFAULT_CARGO_TYPES = [
    {"name": "Crude Oil", "category": "Liquid Bulk"},
    {"name": "Petroleum Products", "category": "Liquid Bulk"},
    {"name": "Chemicals", "category": "Liquid Bulk"},
    {"name": "Containers", "category": "Container"},
    {"name": "General Cargo", "category": "Break Bulk"},
    {"name": "LNG", "category": "Gas"},
]

DEFAULT_BUOYS = [
    {"name": "North Fairway Buoy", "zone_name": "북항"},
    {"name": "South Fairway Buoy", "zone_name": "남항"},
    {"name": "Oil Terminal Approach Buoy", "zone_name": "오일터미널"},
    {"name": "Container Pier Approach Buoy", "zone_name": "컨테이너부두"},
    {"name": "Petrochemical Outer Buoy", "zone_name": "석유화학단지"},
]


async def seed_reference_data(db: AsyncSession) -> None:
    zone_result = await db.scalars(select(PortZone))
    zones = {zone.name: zone for zone in zone_result.all()}
    if not zones:
        for item in DEFAULT_ZONES:
            zone = PortZone(
                name=item["name"],
                zone_type=item["zone_type"],
                description=item["description"],
            )
            db.add(zone)
            zones[zone.name] = zone
        await db.flush()

    existing_cargo_names = set((await db.scalars(select(CargoType.name))).all())
    for item in DEFAULT_CARGO_TYPES:
        if item["name"] in existing_cargo_names:
            continue
        db.add(CargoType(name=item["name"], category=item["category"]))

    existing_buoy_names = set((await db.scalars(select(Buoy.name))).all())
    for item in DEFAULT_BUOYS:
        if item["name"] in existing_buoy_names:
            continue
        zone = zones.get(item["zone_name"])
        if zone is None:
            continue
        db.add(Buoy(name=item["name"], zone_id=zone.zone_id))

    await db.commit()
