import logging

from etl.common import fetch_with_retry, get_http_client, save_raw_snapshot
from etl.config import etl_settings
from etl.database import async_session

logger = logging.getLogger(__name__)

API_URL = f"{etl_settings.upa_api_base}/port/facility/tank-terminal"


async def collect_tank_terminals() -> None:
    logger.info("Collecting tank terminal data")
    try:
        async with get_http_client() as client:
            params = {"serviceKey": etl_settings.upa_api_key, "type": "json"}
            response = await fetch_with_retry(client, API_URL, params=params)
            data = response.json()

        save_raw_snapshot("tank_terminal", data)

        items = _extract_items(data)
        if not items:
            logger.warning("No tank terminal items found")
            return

        async with async_session() as session:
            for item in items:
                await _upsert_terminal(session, item)
            await session.commit()

        logger.info(f"Collected {len(items)} tank terminals")
    except Exception:
        logger.exception("Failed to collect tank terminal data")


def _extract_items(data: dict) -> list[dict]:
    try:
        body = data.get("response", {}).get("body", {})
        items = body.get("items", {}).get("item", [])
        if isinstance(items, dict):
            items = [items]
        return items
    except (AttributeError, TypeError):
        return []


async def _upsert_terminal(session, item: dict) -> None:  # type: ignore[no-untyped-def]
    from sqlalchemy import text

    name = item.get("terminalName", "")
    if not name:
        return

    await session.execute(
        text("""
            INSERT INTO tank_terminal (tank_terminal_id, name, zone_id, capacity_kl, tank_count)
            SELECT
                gen_random_uuid(),
                :name,
                (SELECT zone_id FROM port_zone LIMIT 1),
                :capacity,
                :count
            WHERE NOT EXISTS (SELECT 1 FROM tank_terminal WHERE name = :name)
        """),
        {
            "name": name,
            "capacity": _to_float(item.get("capacity")),
            "count": _to_int(item.get("tankCount")),
        },
    )

    operator_name = item.get("operatorName")
    if operator_name:
        await session.execute(
            text("""
                INSERT INTO operator (operator_id, name, operator_type)
                SELECT gen_random_uuid(), :name, 'tank_terminal'
                WHERE NOT EXISTS (SELECT 1 FROM operator WHERE name = :name)
            """),
            {"name": operator_name},
        )


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
