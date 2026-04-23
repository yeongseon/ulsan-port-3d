import logging
from datetime import datetime, timezone

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.documents import Alert, Insight
from app.models.timeseries import (
    CongestionStat,
    LatestBerthStatus,
    WeatherObservation,
)
from app.services.insight_rules import INSIGHT_RULES, InsightRule

logger = logging.getLogger(__name__)


async def evaluate_rules(session: AsyncSession) -> list[dict]:
    context = await _build_context(session)
    triggered: list[dict] = []

    for rule in INSIGHT_RULES:
        if _check_conditions(rule, context):
            message = _render_message(rule, context)
            insight = {
                "rule_id": rule.rule_id,
                "name": rule.name,
                "severity": rule.severity,
                "message": message,
                "related_entity_type": rule.related_entity_type,
                "context_snapshot": {
                    k: v for k, v in context.items() if isinstance(v, (int, float, str))
                },
            }
            triggered.append(insight)

    return triggered


async def generate_current_insights(session: AsyncSession) -> list[dict]:
    triggered = await evaluate_rules(session)

    results = []
    for item in triggered:
        insight = Insight(
            insight_type=item["rule_id"],
            severity=item["severity"],
            message=item["message"],
            source_data=item["context_snapshot"],
        )
        session.add(insight)
        results.append(
            {
                "insight_id": str(insight.insight_id),
                "type": item["rule_id"],
                "severity": item["severity"],
                "message": item["message"],
                "related_entity_type": item.get("related_entity_type"),
                "source_data": item["context_snapshot"],
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        )

    await session.commit()
    return results


async def _build_context(session: AsyncSession) -> dict:
    context: dict = {}

    weather_row = (
        await session.execute(
            select(WeatherObservation).order_by(WeatherObservation.observed_at.desc()).limit(1)
        )
    ).scalar_one_or_none()

    if weather_row:
        context["wind_speed"] = weather_row.wind_speed or 0
        context["wind_dir"] = weather_row.wind_dir or 0
        context["temperature"] = weather_row.temperature or 0
        context["humidity"] = weather_row.humidity or 0
        context["pressure"] = weather_row.pressure or 0
        context["precipitation"] = weather_row.precipitation or 0
        context["visibility"] = weather_row.visibility or 999
        context["wave_height"] = weather_row.wave_height or 0

    unavailable_count_result = await session.execute(
        select(func.count())
        .select_from(LatestBerthStatus)
        .where(LatestBerthStatus.status == "unavailable")
    )
    context["unavailable_berth_count"] = unavailable_count_result.scalar() or 0

    congestion_row = (
        await session.execute(
            select(CongestionStat).order_by(CongestionStat.stat_date.desc()).limit(1)
        )
    ).scalar_one_or_none()

    if congestion_row:
        context["waiting_count"] = congestion_row.waiting_count or 0
        context["avg_wait_hours"] = congestion_row.avg_wait_hours or 0

    context.setdefault("wind_speed", 0)
    context.setdefault("wave_height", 0)
    context.setdefault("visibility", 999)
    context.setdefault("precipitation", 0)
    context.setdefault("waiting_count", 0)
    context.setdefault("unavailable_berth_count", 0)
    context.setdefault("top_berth_cargo_ratio", 0)
    context.setdefault("top_berth_cargo_pct", 0)

    return context


def _check_conditions(rule: InsightRule, context: dict) -> bool:
    for cond in rule.conditions:
        value = context.get(cond.field)
        if value is None:
            return False
        if cond.operator == ">=" and value < cond.threshold:
            return False
        if cond.operator == "<=" and value > cond.threshold:
            return False
        if cond.operator == ">" and value <= cond.threshold:
            return False
        if cond.operator == "<" and value >= cond.threshold:
            return False
        if cond.operator == "==" and value != cond.threshold:
            return False
    return True


def _render_message(rule: InsightRule, context: dict) -> str:
    try:
        return rule.message_template.format(**context)
    except KeyError:
        return rule.message_template
