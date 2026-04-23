import logging
from typing import Any

from ..common import fetch_with_retry, get_http_client, save_raw_snapshot
from ..config import etl_settings
from ..database import async_session
from ..normalizers import extract_items, to_float, to_int

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

        items = extract_items(data)
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


async def _upsert_terminal(session, item: dict[str, Any]) -> None:  # type: ignore[no-untyped-def]
    from sqlalchemy import text

    name = item.get("terminalName", "")
    if not name:
        return

    zone_name = _resolve_zone_name(item)
    if not zone_name:
        logger.warning("Skipping tank terminal %s because zone name is missing", name)
        return

    await session.execute(
        text("""
            INSERT INTO tank_terminal (tank_terminal_id, name, zone_id, operator_id, capacity_kl, tank_count)
            VALUES (
                gen_random_uuid(),
                :name,
                (
                    SELECT zone_id
                    FROM port_zone
                    WHERE lower(name) = lower(:zone_name)
                    LIMIT 1
                ),
                (
                    SELECT operator_id
                    FROM operator
                    WHERE lower(name) = lower(:operator_name)
                    LIMIT 1
                ),
                :capacity,
                :count
            )
            ON CONFLICT DO NOTHING
        """),
        {
            "name": name,
            "zone_name": zone_name,
            "operator_name": item.get("operatorName"),
            "capacity": to_float(item.get("capacity")),
            "count": to_int(item.get("tankCount")),
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


def _resolve_zone_name(item: dict[str, Any]) -> str | None:
    for key in ("zoneName", "zone", "harborName", "portZoneName"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    search_text = " ".join(
        str(value)
        for value in (item.get("terminalName"), item.get("operatorName"), item.get("detail"))
        if value
    )
    zone_keywords = {
        "북항": "북항",
        "남항": "남항",
        "오일": "오일터미널",
        "터미널": "오일터미널",
        "컨테이너": "컨테이너부두",
        "석유화학": "석유화학단지",
        "petrochemical": "석유화학단지",
        "container": "컨테이너부두",
        "oil": "오일터미널",
        "north": "북항",
        "south": "남항",
    }
    lowered = search_text.lower()
    for keyword, zone_name in zone_keywords.items():
        if keyword.lower() in lowered:
            return zone_name
    return None
