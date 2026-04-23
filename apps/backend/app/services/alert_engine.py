import logging
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.documents import Alert
from app.models.timeseries import (
    CongestionStat,
    LatestBerthStatus,
    WeatherObservation,
)

logger = logging.getLogger(__name__)

WEATHER_THRESHOLDS = {
    "wind_speed_warning": 15.0,
    "wind_speed_critical": 20.0,
    "wave_height_warning": 2.0,
    "wave_height_critical": 3.5,
    "precipitation_warning": 30.0,
    "visibility_warning": 1.0,
}

BERTH_THRESHOLDS = {
    "unavailable_warning": 2,
    "unavailable_critical": 5,
}

CONGESTION_THRESHOLDS = {
    "waiting_warning": 10,
    "waiting_critical": 20,
}


async def evaluate_alerts(session: AsyncSession) -> list[dict]:
    alerts: list[dict] = []

    weather_alerts = await _check_weather_alerts(session)
    alerts.extend(weather_alerts)

    berth_alerts = await _check_berth_alerts(session)
    alerts.extend(berth_alerts)

    congestion_alerts = await _check_congestion_alerts(session)
    alerts.extend(congestion_alerts)

    if weather_alerts and berth_alerts:
        alerts.append(
            {
                "alert_type": "compound",
                "severity": "critical",
                "message": "기상 악화와 선석 사용불가가 동시 발생 중입니다. 복합 위험 상황에 대한 즉시 대응이 필요합니다.",
                "related_entity_type": None,
                "related_entity_id": None,
            }
        )

    for alert_data in alerts:
        alert = Alert(
            alert_type=alert_data["alert_type"],
            severity=alert_data["severity"],
            message=alert_data["message"],
            related_entity_type=alert_data.get("related_entity_type"),
            related_entity_id=alert_data.get("related_entity_id"),
        )
        session.add(alert)

    if alerts:
        await session.commit()

    return alerts


async def _check_weather_alerts(session: AsyncSession) -> list[dict]:
    alerts: list[dict] = []
    row = (
        await session.execute(
            select(WeatherObservation).order_by(WeatherObservation.observed_at.desc()).limit(1)
        )
    ).scalar_one_or_none()

    if not row:
        return alerts

    ws = row.wind_speed or 0
    wh = row.wave_height or 0
    prec = row.precipitation or 0
    vis = row.visibility or 999

    if ws >= WEATHER_THRESHOLDS["wind_speed_critical"]:
        alerts.append(
            {
                "alert_type": "weather",
                "severity": "critical",
                "message": f"풍속 {ws}m/s — 입출항 제한 기준 초과",
                "related_entity_type": "WeatherObservation",
                "related_entity_id": str(row.id),
            }
        )
    elif ws >= WEATHER_THRESHOLDS["wind_speed_warning"]:
        alerts.append(
            {
                "alert_type": "weather",
                "severity": "warning",
                "message": f"풍속 {ws}m/s로 상승 중 — 운항 주의",
                "related_entity_type": "WeatherObservation",
                "related_entity_id": str(row.id),
            }
        )

    if wh >= WEATHER_THRESHOLDS["wave_height_critical"]:
        alerts.append(
            {
                "alert_type": "weather",
                "severity": "critical",
                "message": f"파고 {wh}m — 접안 작업 중단 권고",
                "related_entity_type": "WeatherObservation",
                "related_entity_id": str(row.id),
            }
        )
    elif wh >= WEATHER_THRESHOLDS["wave_height_warning"]:
        alerts.append(
            {
                "alert_type": "weather",
                "severity": "warning",
                "message": f"파고 {wh}m 상승 — 접안 주의",
                "related_entity_type": "WeatherObservation",
                "related_entity_id": str(row.id),
            }
        )

    if prec >= WEATHER_THRESHOLDS["precipitation_warning"]:
        alerts.append(
            {
                "alert_type": "weather",
                "severity": "warning",
                "message": f"강수량 {prec}mm — 하역작업 지연 예상",
                "related_entity_type": "WeatherObservation",
                "related_entity_id": str(row.id),
            }
        )

    if vis <= WEATHER_THRESHOLDS["visibility_warning"]:
        alerts.append(
            {
                "alert_type": "weather",
                "severity": "warning",
                "message": f"시정 {vis}km — 저시정 운항 제한",
                "related_entity_type": "WeatherObservation",
                "related_entity_id": str(row.id),
            }
        )

    return alerts


async def _check_berth_alerts(session: AsyncSession) -> list[dict]:
    alerts: list[dict] = []
    count_result = await session.execute(
        select(func.count())
        .select_from(LatestBerthStatus)
        .where(LatestBerthStatus.status == "unavailable")
    )
    count = count_result.scalar() or 0

    if count >= BERTH_THRESHOLDS["unavailable_critical"]:
        alerts.append(
            {
                "alert_type": "berth",
                "severity": "critical",
                "message": f"사용불가 선석 {count}개 — 비상 운영 계획 가동 필요",
                "related_entity_type": "Berth",
                "related_entity_id": None,
            }
        )
    elif count >= BERTH_THRESHOLDS["unavailable_warning"]:
        alerts.append(
            {
                "alert_type": "berth",
                "severity": "warning",
                "message": f"사용불가 선석 {count}개 — 접안 계획 조정 필요",
                "related_entity_type": "Berth",
                "related_entity_id": None,
            }
        )

    return alerts


async def _check_congestion_alerts(session: AsyncSession) -> list[dict]:
    alerts: list[dict] = []
    row = (
        await session.execute(
            select(CongestionStat).order_by(CongestionStat.stat_date.desc()).limit(1)
        )
    ).scalar_one_or_none()

    if not row:
        return alerts

    wc = row.waiting_count or 0

    if wc >= CONGESTION_THRESHOLDS["waiting_critical"]:
        alerts.append(
            {
                "alert_type": "congestion",
                "severity": "critical",
                "message": f"체선 {wc}척 — 항만 운영 병목 심각",
                "related_entity_type": "CongestionStat",
                "related_entity_id": str(row.id),
            }
        )
    elif wc >= CONGESTION_THRESHOLDS["waiting_warning"]:
        alerts.append(
            {
                "alert_type": "congestion",
                "severity": "warning",
                "message": f"체선 {wc}척 — 체선 심화 경고",
                "related_entity_type": "CongestionStat",
                "related_entity_id": str(row.id),
            }
        )

    return alerts
