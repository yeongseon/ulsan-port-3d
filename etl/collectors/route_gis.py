import logging
import json
from typing import Any, cast

from ..common import fetch_with_retry, get_http_client, save_raw_snapshot
from ..config import etl_settings
from ..database import async_session
from ..normalizers import extract_items, to_float

logger = logging.getLogger(__name__)

API_URL = f"{etl_settings.upa_api_base}/port/facility/route"


async def collect_route_gis() -> None:
    logger.info("Collecting route GIS data")
    try:
        async with get_http_client() as client:
            params = {"serviceKey": etl_settings.upa_api_key, "type": "json"}
            response = await fetch_with_retry(client, API_URL, params=params)
            data = response.json()

        save_raw_snapshot("route_gis", data)

        items = extract_items(data)
        if not items:
            logger.warning("No route GIS items found")
            return

        async with async_session() as session:
            for item in items:
                await _upsert_route(session, item)
            await session.commit()

        logger.info(f"Collected {len(items)} route segments")
    except Exception:
        logger.exception("Failed to collect route GIS data")


async def _upsert_route(session, item: dict[str, Any]) -> None:  # type: ignore[no-untyped-def]
    from sqlalchemy import text

    name = item.get("routeName", "")
    if not name:
        return

    zone_name = _extract_zone_name(item)
    if not zone_name:
        logger.warning("Skipping route %s because zone name is missing", name)
        return

    geometry_wkt = _build_linestring_wkt(item)
    await session.execute(
        text("""
            INSERT INTO route_segment (segment_id, name, zone_id, geometry, width, direction)
            VALUES (
                gen_random_uuid(),
                :name,
                (
                    SELECT zone_id
                    FROM port_zone
                    WHERE lower(name) = lower(:zone_name)
                    LIMIT 1
                ),
                CASE
                    WHEN :geometry_wkt IS NOT NULL THEN ST_GeomFromText(:geometry_wkt, 4326)
                    ELSE NULL
                END,
                :width,
                :direction
            )
            ON CONFLICT DO NOTHING
        """),
        {
            "name": name,
            "zone_name": zone_name,
            "geometry_wkt": geometry_wkt,
            "width": to_float(item.get("width")),
            "direction": item.get("direction"),
        },
    )


def _extract_zone_name(item: dict[str, Any]) -> str | None:
    for key in ("zoneName", "zone", "harborName", "portZoneName"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _build_linestring_wkt(item: dict[str, Any]) -> str | None:
    for key in (
        "geometry",
        "routeGeometry",
        "path",
        "routePath",
        "coordinates",
        "routeCoordinates",
    ):
        value = item.get(key)
        coordinates = _parse_coordinates(value)
        if coordinates:
            return _to_linestring_wkt(coordinates)

    lat_lon_pairs = _parse_lat_lon_lists(item)
    if lat_lon_pairs:
        return _to_linestring_wkt(lat_lon_pairs)

    start_lat = to_float(item.get("startLat") or item.get("fromLat"))
    start_lon = to_float(item.get("startLon") or item.get("fromLon"))
    end_lat = to_float(item.get("endLat") or item.get("toLat"))
    end_lon = to_float(item.get("endLon") or item.get("toLon"))
    if None not in (start_lat, start_lon, end_lat, end_lon):
        start_lat = cast(float, start_lat)
        start_lon = cast(float, start_lon)
        end_lat = cast(float, end_lat)
        end_lon = cast(float, end_lon)
        return _to_linestring_wkt(
            [(float(start_lon), float(start_lat)), (float(end_lon), float(end_lat))]
        )

    return None


def _parse_coordinates(value: Any) -> list[tuple[float, float]] | None:
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.upper().startswith("LINESTRING"):
            return _parse_linestring_wkt(stripped)
        try:
            value = json.loads(stripped)
        except json.JSONDecodeError:
            return None

    if isinstance(value, dict):
        if value.get("type") == "LineString":
            return _normalize_pairs(value.get("coordinates"))
        return _parse_coordinates(value.get("coordinates") or value.get("path"))

    if isinstance(value, list):
        return _normalize_pairs(value)

    return None


def _parse_lat_lon_lists(item: dict[str, Any]) -> list[tuple[float, float]] | None:
    lat_values = _parse_number_list(
        item.get("latList") or item.get("lats") or item.get("latitudeList")
    )
    lon_values = _parse_number_list(
        item.get("lonList") or item.get("lons") or item.get("longitudeList")
    )
    if lat_values and lon_values and len(lat_values) == len(lon_values):
        return list(zip(lon_values, lat_values))
    return None


def _parse_number_list(value: Any) -> list[float] | None:
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        parts = [part.strip() for part in stripped.replace(";", ",").split(",")]
        numbers = [to_float(part) for part in parts if part]
        return [number for number in numbers if number is not None] or None
    if isinstance(value, list):
        numbers = [to_float(part) for part in value]
        return [number for number in numbers if number is not None] or None
    return None


def _normalize_pairs(value: Any) -> list[tuple[float, float]] | None:
    if not isinstance(value, list):
        return None

    pairs: list[tuple[float, float]] = []
    for item in value:
        if isinstance(item, dict):
            lon = to_float(item.get("lon") or item.get("x") or item.get("lng"))
            lat = to_float(item.get("lat") or item.get("y"))
        elif isinstance(item, (list, tuple)) and len(item) >= 2:
            lon = to_float(item[0])
            lat = to_float(item[1])
        else:
            continue
        if lon is not None and lat is not None:
            pairs.append((lon, lat))

    return pairs if len(pairs) >= 2 else None


def _parse_linestring_wkt(value: str) -> list[tuple[float, float]] | None:
    prefix = "LINESTRING("
    if not value.upper().startswith(prefix):
        return None
    body = value[len(prefix) : -1]
    pairs: list[tuple[float, float]] = []
    for part in body.split(","):
        components = [component for component in part.strip().split() if component]
        if len(components) < 2:
            continue
        lon = to_float(components[0])
        lat = to_float(components[1])
        if lon is not None and lat is not None:
            pairs.append((lon, lat))
    return pairs if len(pairs) >= 2 else None


def _to_linestring_wkt(coordinates: list[tuple[float, float]]) -> str | None:
    if len(coordinates) < 2:
        return None
    points = ", ".join(f"{lon} {lat}" for lon, lat in coordinates)
    return f"LINESTRING({points})"
