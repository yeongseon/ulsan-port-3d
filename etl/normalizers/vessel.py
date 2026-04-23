from typing import Any, TypedDict

from .common import clean_string, to_float


class VesselPositionRecord(TypedDict):
    vessel_id: str
    name: str | None
    call_sign: str | None
    lat: float
    lon: float
    speed: float | None
    course: float | None
    heading: float | None
    draft: float | None


def normalize_vessel_position_items(items: list[dict[str, Any]]) -> list[VesselPositionRecord]:
    normalized: list[VesselPositionRecord] = []
    for item in items:
        call_sign = clean_string(item.get("callSign"))
        vessel_name = clean_string(item.get("vesselName"))
        vessel_id = call_sign or vessel_name or "unknown"

        normalized.append(
            {
                "vessel_id": vessel_id,
                "name": vessel_name,
                "call_sign": call_sign,
                "lat": to_float(item.get("lat")) or 0.0,
                "lon": to_float(item.get("lon")) or 0.0,
                "speed": to_float(item.get("speed")),
                "course": to_float(item.get("course")),
                "heading": to_float(item.get("heading")),
                "draft": to_float(item.get("draft")),
            }
        )
    return normalized
