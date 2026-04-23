from app.schemas.common import APIModel


class VesselLiveResponse(APIModel):
    vessel_id: str
    name: str | None
    call_sign: str | None
    imo: str | None
    ship_type: str | None
    gross_tonnage: float | None
    lat: float
    lon: float
    speed: float | None
    course: float | None
    heading: float | None
    draft: float | None
    observed_at: str
    updated_at: str | None


class VesselEventResponse(APIModel):
    event_id: str
    vessel_id: str
    call_sign: str | None
    event_type: str
    berth_facility_code: str | None
    event_time: str
    detail: str | None
    raw_data: str | None
    created_at: str | None


class VesselDetailResponse(APIModel):
    vessel_id: str
    latest_position: VesselLiveResponse
    events: list[VesselEventResponse]
