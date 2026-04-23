import logging

from etl.common import fetch_with_retry, get_http_client, save_raw_snapshot
from etl.config import etl_settings
from etl.database import async_session
from etl.normalizers import clean_string, extract_items

logger = logging.getLogger(__name__)

API_URL = f"{etl_settings.upa_api_base}/port/vessel/event"

EVENT_TYPE_MAP = {
    "입항": "arrival",
    "출항": "departure",
    "접안": "berthing",
    "이안": "unberthing",
}


async def collect_vessel_events() -> None:
    logger.info("Collecting vessel events")
    try:
        async with get_http_client() as client:
            params = {"serviceKey": etl_settings.upa_api_key, "type": "json"}
            response = await fetch_with_retry(client, API_URL, params=params)
            data = response.json()

        save_raw_snapshot("vessel_event", data)

        items = extract_items(data)
        if not items:
            logger.warning("No vessel event items found")
            return

        async with async_session() as session:
            for item in items:
                await _insert_event(session, item)
            await session.commit()

        logger.info(f"Collected {len(items)} vessel events")
    except Exception:
        logger.exception("Failed to collect vessel events")


async def _insert_event(session, item: dict[str, object]) -> None:  # type: ignore[no-untyped-def]
    from sqlalchemy import text
    import uuid

    vessel_id = (
        f"{item.get('callSign', '')}_{item.get('arrivalYear', '')}_{item.get('voyageNo', '')}"
    )
    event_type_kr = clean_string(item.get("eventType")) or ""
    event_type = EVENT_TYPE_MAP.get(event_type_kr, event_type_kr)

    await session.execute(
        text("""
            INSERT INTO vessel_event
                (event_id, vessel_id, call_sign, event_type, berth_facility_code, event_time, detail, raw_data)
            VALUES
                (:event_id, :vessel_id, :call_sign, :event_type, :berth_code, NOW(), :detail, :raw_data)
        """),
        {
            "event_id": str(uuid.uuid4()),
            "vessel_id": vessel_id,
            "call_sign": item.get("callSign"),
            "event_type": event_type,
            "berth_code": item.get("berthCode"),
            "detail": item.get("detail"),
            "raw_data": str(item),
        },
    )
