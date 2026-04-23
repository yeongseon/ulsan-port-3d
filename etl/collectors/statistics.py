import logging

from etl.common import fetch_with_retry, get_http_client, save_raw_snapshot
from etl.config import etl_settings
from etl.database import async_session

logger = logging.getLogger(__name__)

ARRIVALS_URL = f"{etl_settings.upa_api_base}/port/stats/arrivals"
LIQUID_CARGO_URL = f"{etl_settings.upa_api_base}/port/stats/liquid-cargo"
CONGESTION_URL = f"{etl_settings.upa_api_base}/port/stats/congestion"


async def collect_statistics() -> None:
    logger.info("Collecting statistics")
    try:
        async with get_http_client() as client:
            params = {"serviceKey": etl_settings.upa_api_key, "type": "json"}

            arrivals_resp = await fetch_with_retry(client, ARRIVALS_URL, params=params)
            arrivals_data = arrivals_resp.json()
            save_raw_snapshot("stats_arrivals", arrivals_data)

            cargo_resp = await fetch_with_retry(client, LIQUID_CARGO_URL, params=params)
            cargo_data = cargo_resp.json()
            save_raw_snapshot("stats_liquid_cargo", cargo_data)

            congestion_resp = await fetch_with_retry(client, CONGESTION_URL, params=params)
            congestion_data = congestion_resp.json()
            save_raw_snapshot("stats_congestion", congestion_data)

        async with async_session() as session:
            await _insert_arrivals(session, arrivals_data)
            await _insert_liquid_cargo(session, cargo_data)
            await _insert_congestion(session, congestion_data)
            await session.commit()

        logger.info("Statistics collected successfully")
    except Exception:
        logger.exception("Failed to collect statistics")


async def _insert_arrivals(session, data: dict) -> None:  # type: ignore[no-untyped-def]
    from sqlalchemy import text

    for item in _extract_items(data):
        await session.execute(
            text("""
                INSERT INTO arrival_stat_monthly (year_month, zone_name, berth_name, vessel_count)
                VALUES (:ym, :zone, :berth, :count)
            """),
            {
                "ym": item.get("yearMonth", ""),
                "zone": item.get("zoneName"),
                "berth": item.get("berthName"),
                "count": _to_int(item.get("vesselCount")),
            },
        )


async def _insert_liquid_cargo(session, data: dict) -> None:  # type: ignore[no-untyped-def]
    from sqlalchemy import text

    for item in _extract_items(data):
        await session.execute(
            text("""
                INSERT INTO cargo_stat_monthly (year_month, zone_name, berth_name, cargo_type, volume_ton)
                VALUES (:ym, :zone, :berth, :cargo, :vol)
            """),
            {
                "ym": item.get("yearMonth", ""),
                "zone": item.get("zoneName"),
                "berth": item.get("berthName"),
                "cargo": item.get("cargoType"),
                "vol": _to_float(item.get("volumeTon")),
            },
        )


async def _insert_congestion(session, data: dict) -> None:  # type: ignore[no-untyped-def]
    from sqlalchemy import text

    for item in _extract_items(data):
        await session.execute(
            text("""
                INSERT INTO congestion_stat (stat_date, waiting_count, avg_wait_hours)
                VALUES (:date, :count, :hours)
            """),
            {
                "date": item.get("statDate", ""),
                "count": _to_int(item.get("waitingCount")),
                "hours": _to_float(item.get("avgWaitHours")),
            },
        )


def _extract_items(data: dict) -> list[dict]:
    try:
        body = data.get("response", {}).get("body", {})
        items = body.get("items", {}).get("item", [])
        if isinstance(items, dict):
            items = [items]
        return items
    except (AttributeError, TypeError):
        return []


def _to_float(val) -> float | None:  # type: ignore[no-untyped-def]
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _to_int(val) -> int | None:  # type: ignore[no-untyped-def]
    if val is None:
        return None
    try:
        return int(val)
    except (ValueError, TypeError):
        return None
