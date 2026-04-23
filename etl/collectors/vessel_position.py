import logging
from typing import Any

from ..common import fetch_with_retry, get_http_client, save_raw_snapshot
from ..config import etl_settings
from ..database import async_session
from ..normalizers import extract_items, normalize_vessel_position_items
from ..normalizers.vessel import VesselPositionRecord

logger = logging.getLogger(__name__)

API_URL = f"{etl_settings.upa_api_base}/port/vessel/position"


async def collect_vessel_positions() -> None:
    logger.info("Collecting vessel positions")
    try:
        async with get_http_client() as client:
            params = {"serviceKey": etl_settings.upa_api_key, "type": "json"}
            response = await fetch_with_retry(client, API_URL, params=params)
            data = response.json()

        save_raw_snapshot("vessel_position", data)

        raw_items = extract_items(data)
        items = normalize_vessel_position_items(raw_items)
        if not items:
            logger.warning("No vessel position items found")
            return

        async with async_session() as session:
            for item in items:
                await _upsert_position(session, item)
            await session.commit()

        logger.info(f"Collected {len(items)} vessel positions")
    except Exception:
        logger.exception("Failed to collect vessel positions")


async def _upsert_position(session, item: VesselPositionRecord) -> None:  # type: ignore[no-untyped-def]
    from sqlalchemy import text

    await session.execute(
        text("""
            INSERT INTO latest_vessel_position
                (vessel_id, name, call_sign, lat, lon, speed, course, heading, draft, observed_at, updated_at)
            VALUES
                (:vessel_id, :name, :call_sign, :lat, :lon, :speed, :course, :heading, :draft, NOW(), NOW())
            ON CONFLICT (vessel_id) DO UPDATE SET
                name = EXCLUDED.name,
                lat = EXCLUDED.lat,
                lon = EXCLUDED.lon,
                speed = EXCLUDED.speed,
                course = EXCLUDED.course,
                heading = EXCLUDED.heading,
                draft = EXCLUDED.draft,
                observed_at = NOW(),
                updated_at = NOW()
        """),
        {
            "vessel_id": item["vessel_id"],
            "name": item.get("name"),
            "call_sign": item.get("call_sign"),
            "lat": item["lat"],
            "lon": item["lon"],
            "speed": item.get("speed"),
            "course": item.get("course"),
            "heading": item.get("heading"),
            "draft": item.get("draft"),
        },
    )

    await session.execute(
        text("""
            INSERT INTO vessel_position
                (vessel_id, name, call_sign, lat, lon, speed, course, heading, draft, observed_at)
            VALUES
                (:vessel_id, :name, :call_sign, :lat, :lon, :speed, :course, :heading, :draft, NOW())
        """),
        {
            "vessel_id": item["vessel_id"],
            "name": item.get("name"),
            "call_sign": item.get("call_sign"),
            "lat": item["lat"],
            "lon": item["lon"],
            "speed": item.get("speed"),
            "course": item.get("course"),
            "heading": item.get("heading"),
            "draft": item.get("draft"),
        },
    )
