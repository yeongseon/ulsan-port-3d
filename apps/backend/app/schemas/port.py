from app.schemas.common import APIModel


class PortOverviewResponse(APIModel):
    name: str
    zone_count: int
    berth_count: int
    active_vessel_count: int
    alert_count: int
    last_updated: str | None


class ZoneResponse(APIModel):
    zone_id: str
    name: str
    zone_type: str
    description: str | None
    berth_count: int
    buoy_count: int
    created_at: str | None
