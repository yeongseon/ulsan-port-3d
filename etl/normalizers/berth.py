from typing import Any, TypedDict

from .common import clean_string, extract_zone_name, to_float


class BerthFacilityRecord(TypedDict):
    facility_code: str
    name: str
    zone_name: str | None
    length: float | None
    depth: float | None
    lat: float | None
    lon: float | None


def normalize_berth_facility_items(items: list[dict[str, Any]]) -> list[BerthFacilityRecord]:
    normalized: list[BerthFacilityRecord] = []
    for item in items:
        facility_code = clean_string(item.get("facilityCode"))
        if not facility_code:
            continue

        normalized.append(
            {
                "facility_code": facility_code,
                "name": clean_string(item.get("berthName")) or "",
                "zone_name": extract_zone_name(item),
                "length": to_float(item.get("berthLength")),
                "depth": to_float(item.get("berthDepth")),
                "lat": to_float(item.get("lat")),
                "lon": to_float(item.get("lon")),
            }
        )
    return normalized
