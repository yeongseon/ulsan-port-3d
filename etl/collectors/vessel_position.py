import logging

from etl.common import fetch_with_retry, get_http_client, save_raw_snapshot
from etl.config import etl_settings
from etl.database import async_session

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

        items = _extract_items(data)
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


def _extract_items(data: dict) -> list[dict]:
    try:
        body = data.get("response", {}).get("body", {})
        items = body.get("items", {}).get("item", [])
        if isinstance(items, dict):
            items = [items]
        return items
    except (AttributeError, TypeError):
        return []


async def _upsert_position(session, item: dict) -> None:  # type: ignore[no-untyped-def]
    from sqlalchemy import text

    # Position data does not include arrival year or voyage number, so call sign is the
    # most stable identifier available for matching the AGENTS.md vessel identity convention.
    vessel_id = item.get("callSign", "") or item.get("vesselName", "unknown")
    lat = float(item.get("lat", 0))
    lon = float(item.get("lon", 0))

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
            "vessel_id": vessel_id,
            "name": item.get("vesselName"),
            "call_sign": item.get("callSign"),
            "lat": lat,
            "lon": lon,
            "speed": _to_float(item.get("speed")),
            "course": _to_float(item.get("course")),
            "heading": _to_float(item.get("heading")),
            "draft": _to_float(item.get("draft")),
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
            "vessel_id": vessel_id,
            "name": item.get("vesselName"),
            "call_sign": item.get("callSign"),
            "lat": lat,
            "lon": lon,
            "speed": _to_float(item.get("speed")),
            "course": _to_float(item.get("course")),
            "heading": _to_float(item.get("heading")),
            "draft": _to_float(item.get("draft")),
        },
    )


def _to_float(val: str | float | None) -> float | None:
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None
