from app.schemas.common import APIModel


class BerthResponse(APIModel):
    berth_id: str
    facility_code: str
    name: str
    zone_id: str
    zone_name: str
    operator_id: str | None
    operator_name: str | None
    length: float | None
    depth: float | None
    latitude: float | None
    longitude: float | None
    latest_status: str | None
    latest_status_detail: str | None
    latest_status_updated_at: str | None
    created_at: str | None


class BerthStatusResponse(APIModel):
    berth_facility_code: str
    berth_name: str | None
    zone_name: str | None
    status: str
    status_detail: str | None
    updated_at: str | None
