import logging

from etl.common import fetch_with_retry, get_http_client, save_raw_snapshot
from etl.config import etl_settings
from etl.database import async_session

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


def _extract_items(data: dict) -> list[dict]:
    try:
        body = data.get("response", {}).get("body", {})
        items = body.get("items", {}).get("item", [])
        if isinstance(items, dict):
            items = [items]
        return items
    except (AttributeError, TypeError):
        return []


async def _upsert_berth(session, item: dict) -> None:  # type: ignore[no-untyped-def]
    from sqlalchemy import text

    facility_code = item.get("facilityCode", "")
    if not facility_code:
        return

    lat = _to_float(item.get("lat"))
    lon = _to_float(item.get("lon"))

    await session.execute(
        text("""
            INSERT INTO berth (berth_id, facility_code, name, zone_id, length, depth)
            SELECT
                gen_random_uuid(),
                :facility_code,
                :name,
                (SELECT zone_id FROM port_zone LIMIT 1),
                :length,
                :depth
            WHERE NOT EXISTS (SELECT 1 FROM berth WHERE facility_code = :facility_code)
        """),
        {
            "facility_code": facility_code,
            "name": item.get("berthName", ""),
            "length": _to_float(item.get("berthLength")),
            "depth": _to_float(item.get("berthDepth")),
        },
    )


def _to_float(val) -> float | None:  # type: ignore[no-untyped-def]
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None
