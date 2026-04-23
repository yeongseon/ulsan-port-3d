from app.schemas.common import APIModel


class ScenarioSummaryResponse(APIModel):
    scenario_id: str
    frame_count: int
    first_frame_index: int | None
    last_frame_index: int | None
    first_timestamp: str | None
    last_timestamp: str | None
    is_simulated: bool


class ScenarioFrameResponse(APIModel):
    frame_id: str
    scenario_id: str
    frame_index: int
    timestamp: str
    vessel_positions: dict | None
    berth_statuses: dict | None
    weather: dict | None
    alerts: dict | None
    ai_summary: str | None
    is_simulated: bool
    created_at: str | None


class AlertResponse(APIModel):
    alert_id: str
    alert_type: str
    severity: str
    message: str
    related_entity_type: str | None
    related_entity_id: str | None
    is_active: bool
    created_at: str | None
