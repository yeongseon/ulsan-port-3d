import logging

from etl.common import fetch_with_retry, get_http_client, save_raw_snapshot
from etl.config import etl_settings
from etl.database import async_session

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

        items = _extract_items(data)
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


def _extract_items(data: dict) -> list[dict]:
    try:
        body = data.get("response", {}).get("body", {})
        items = body.get("items", {}).get("item", [])
        if isinstance(items, dict):
            items = [items]
        return items
    except (AttributeError, TypeError):
        return []


async def _upsert_route(session, item: dict) -> None:  # type: ignore[no-untyped-def]
    from sqlalchemy import text

    name = item.get("routeName", "")
    await session.execute(
        text("""
            INSERT INTO route_segment (segment_id, name, zone_id, width, direction)
            SELECT
                gen_random_uuid(),
                :name,
                (SELECT zone_id FROM port_zone LIMIT 1),
                :width,
                :direction
            WHERE NOT EXISTS (SELECT 1 FROM route_segment WHERE name = :name)
        """),
        {
            "name": name,
            "width": _to_float(item.get("width")),
            "direction": item.get("direction"),
        },
    )


def _to_float(val) -> float | None:  # type: ignore[no-untyped-def]
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None
