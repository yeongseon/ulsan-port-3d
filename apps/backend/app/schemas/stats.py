from app.schemas.common import APIModel


class ArrivalStatResponse(APIModel):
    year_month: str
    zone_name: str | None
    berth_name: str | None
    vessel_count: int | None
    created_at: str | None


class LiquidCargoStatResponse(APIModel):
    year_month: str
    zone_name: str | None
    berth_name: str | None
    cargo_type: str | None
    volume_ton: float | None
    created_at: str | None


class CongestionStatResponse(APIModel):
    stat_date: str
    waiting_count: int | None
    avg_wait_hours: float | None
    created_at: str | None
