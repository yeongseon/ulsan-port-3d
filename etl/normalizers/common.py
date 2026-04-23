from collections.abc import Mapping
from typing import Any


def extract_items(data: Mapping[str, Any]) -> list[dict[str, Any]]:
    try:
        body = data.get("response", {}).get("body", {})
        items = body.get("items", {}).get("item", [])
    except AttributeError:
        return []

    if isinstance(items, Mapping):
        return [dict(items)]
    if isinstance(items, list):
        return [dict(item) for item in items if isinstance(item, Mapping)]
    return []


def clean_string(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    cleaned = value.strip()
    return cleaned or None


def to_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def to_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def extract_zone_name(item: Mapping[str, Any]) -> str | None:
    for key in ("zoneName", "zone", "harborName", "portZoneName"):
        zone_name = clean_string(item.get(key))
        if zone_name:
            return zone_name
    return None
