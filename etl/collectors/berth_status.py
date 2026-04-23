import logging

from etl.common import fetch_with_retry, get_http_client, save_raw_snapshot
from etl.config import etl_settings
from etl.database import async_session
from etl.normalizers import clean_string, extract_items

logger = logging.getLogger(__name__)

API_URL = f"{etl_settings.upa_api_base}/port/berth/status"

STATUS_MAP = {
    "정상": "normal",
    "일부파손": "damaged",
    "사용불가": "unavailable",
    "확인중": "checking",
}


async def collect_berth_status() -> None:
    logger.info("Collecting berth status")
    try:
        async with get_http_client() as client:
            params = {"serviceKey": etl_settings.upa_api_key, "type": "json"}
            response = await fetch_with_retry(client, API_URL, params=params)
            data = response.json()

        save_raw_snapshot("berth_status", data)

        items = extract_items(data)
        if not items:
            logger.warning("No berth status items found")
            return

        async with async_session() as session:
            for item in items:
                await _upsert_status(session, item)
            await session.commit()

        logger.info(f"Collected {len(items)} berth statuses")
    except Exception:
        logger.exception("Failed to collect berth status")


async def _upsert_status(session, item: dict[str, object]) -> None:  # type: ignore[no-untyped-def]
    from sqlalchemy import text

    facility_code = item.get("facilityCode", "")
    if not facility_code:
        return

    status_kr = clean_string(item.get("status")) or "확인중"
    status = STATUS_MAP.get(status_kr, "checking")

    await session.execute(
        text("""
            INSERT INTO latest_berth_status
                (berth_facility_code, berth_name, zone_name, status, status_detail, updated_at)
            VALUES
                (:code, :name, :zone, :status, :detail, NOW())
            ON CONFLICT (berth_facility_code) DO UPDATE SET
                status = EXCLUDED.status,
                status_detail = EXCLUDED.status_detail,
                updated_at = NOW()
        """),
        {
            "code": facility_code,
            "name": item.get("berthName"),
            "zone": item.get("zoneName"),
            "status": status,
            "detail": item.get("statusDetail"),
        },
    )

    await session.execute(
        text("""
            INSERT INTO berth_status
                (berth_facility_code, status, status_detail, observed_at)
            VALUES
                (:code, :status, :detail, NOW())
        """),
        {
            "code": facility_code,
            "status": status,
            "detail": item.get("statusDetail"),
        },
    )
