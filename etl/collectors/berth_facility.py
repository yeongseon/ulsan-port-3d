import logging
from typing import Any

from ..common import fetch_with_retry, get_http_client, save_raw_snapshot
from ..config import etl_settings
from ..database import async_session

logger = logging.getLogger(__name__)

API_URL = f"{etl_settings.upa_api_base}/port/facility/berth"


async def collect_berth_facilities() -> None:
    logger.info("Collecting berth facility information")
    try:
        async with get_http_client() as client:
            params = {"serviceKey": etl_settings.upa_api_key, "type": "json"}
            response = await fetch_with_retry(client, API_URL, params=params)
            data = response.json()

        save_raw_snapshot("berth_facility", data)

        items = _extract_items(data)
        if not items:
            logger.warning("No berth facility items found")
            return

        async with async_session() as session:
            for item in items:
                await _upsert_berth(session, item)
            await session.commit()

        logger.info(f"Collected {len(items)} berth facilities")
    except Exception:
        logger.exception("Failed to collect berth facilities")


def _extract_items(data: dict[str, Any]) -> list[dict[str, Any]]:
    try:
        body = data.get("response", {}).get("body", {})
        items = body.get("items", {}).get("item", [])
        if isinstance(items, dict):
            items = [items]
        return items
    except (AttributeError, TypeError):
        return []


async def _upsert_berth(session, item: dict[str, Any]) -> None:  # type: ignore[no-untyped-def]
    from sqlalchemy import text

    facility_code = item.get("facilityCode", "")
    if not facility_code:
        return

    lat = _to_float(item.get("lat"))
    lon = _to_float(item.get("lon"))
    zone_name = _extract_zone_name(item)
    if not zone_name:
        logger.warning("Skipping berth %s because zone name is missing", facility_code)
        return

    await session.execute(
        text("""
            INSERT INTO berth (berth_id, facility_code, name, zone_id, length, depth, geometry)
            VALUES (
                gen_random_uuid(),
                :facility_code,
                :name,
                (
                    SELECT zone_id
                    FROM port_zone
                    WHERE lower(name) = lower(:zone_name)
                    LIMIT 1
                ),
                :length,
                :depth,
                CASE
                    WHEN :lat IS NOT NULL AND :lon IS NOT NULL
                    THEN ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)
                    ELSE NULL
                END
            )
            ON CONFLICT (facility_code) DO UPDATE SET
                name = EXCLUDED.name,
                zone_id = COALESCE(EXCLUDED.zone_id, berth.zone_id),
                length = EXCLUDED.length,
                depth = EXCLUDED.depth,
                geometry = COALESCE(EXCLUDED.geometry, berth.geometry)
        """),
        {
            "facility_code": facility_code,
            "name": item.get("berthName", ""),
            "zone_name": zone_name,
            "length": _to_float(item.get("berthLength")),
            "depth": _to_float(item.get("berthDepth")),
            "lat": lat,
            "lon": lon,
        },
    )


def _extract_zone_name(item: dict[str, Any]) -> str | None:
    for key in ("zoneName", "zone", "harborName", "portZoneName"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _to_float(val) -> float | None:  # type: ignore[no-untyped-def]
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None
