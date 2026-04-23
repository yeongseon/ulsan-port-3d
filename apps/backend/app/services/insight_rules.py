from dataclasses import dataclass


@dataclass
class RuleCondition:
    field: str
    operator: str
    threshold: float


@dataclass
class InsightRule:
    rule_id: str
    name: str
    conditions: list[RuleCondition]
    message_template: str
    severity: str
    related_entity_type: str | None = None


INSIGHT_RULES: list[InsightRule] = [
    InsightRule(
        rule_id="wind_high",
        name="High Wind Speed",
        conditions=[RuleCondition("wind_speed", ">=", 15.0)],
        message_template="내항 풍속이 {wind_speed}m/s로 상승하여 운항 주의가 필요합니다.",
        severity="warning",
        related_entity_type="WeatherObservation",
    ),
    InsightRule(
        rule_id="wind_critical",
        name="Critical Wind Speed",
        conditions=[RuleCondition("wind_speed", ">=", 20.0)],
        message_template="풍속 {wind_speed}m/s — 입출항 제한 기준 초과. 즉시 조치가 필요합니다.",
        severity="critical",
        related_entity_type="WeatherObservation",
    ),
    InsightRule(
        rule_id="wave_high",
        name="High Wave",
        conditions=[RuleCondition("wave_height", ">=", 2.0)],
        message_template="파고 {wave_height}m로 상승 중입니다. 접안 작업 시 주의가 필요합니다.",
        severity="warning",
        related_entity_type="WeatherObservation",
    ),
    InsightRule(
        rule_id="berth_unavailable_multiple",
        name="Multiple Berths Unavailable",
        conditions=[RuleCondition("unavailable_berth_count", ">=", 2)],
        message_template="현재 {unavailable_berth_count}개 선석이 사용불가 상태입니다. 접안 계획 조정이 필요합니다.",
        severity="warning",
        related_entity_type="Berth",
    ),
    InsightRule(
        rule_id="berth_unavailable_critical",
        name="Many Berths Unavailable",
        conditions=[RuleCondition("unavailable_berth_count", ">=", 5)],
        message_template="사용불가 선석이 {unavailable_berth_count}개로 심각한 상황입니다. 비상 운영 계획을 가동하십시오.",
        severity="critical",
        related_entity_type="Berth",
    ),
    InsightRule(
        rule_id="congestion_high",
        name="High Congestion",
        conditions=[RuleCondition("waiting_count", ">=", 10)],
        message_template="체선 선박 {waiting_count}척 — 체선이 심화되고 있습니다.",
        severity="warning",
        related_entity_type="CongestionStat",
    ),
    InsightRule(
        rule_id="congestion_critical",
        name="Critical Congestion",
        conditions=[RuleCondition("waiting_count", ">=", 20)],
        message_template="체선 선박 {waiting_count}척으로 항만 운영 병목이 발생했습니다.",
        severity="critical",
        related_entity_type="CongestionStat",
    ),
    InsightRule(
        rule_id="visibility_low",
        name="Low Visibility",
        conditions=[RuleCondition("visibility", "<=", 1.0)],
        message_template="시정 {visibility}km — 저시정으로 인한 운항 제한이 예상됩니다.",
        severity="warning",
        related_entity_type="WeatherObservation",
    ),
    InsightRule(
        rule_id="heavy_rain",
        name="Heavy Precipitation",
        conditions=[RuleCondition("precipitation", ">=", 30.0)],
        message_template="강수량 {precipitation}mm — 강우로 인한 하역작업 지연이 예상됩니다.",
        severity="warning",
        related_entity_type="WeatherObservation",
    ),
    InsightRule(
        rule_id="cargo_concentration",
        name="Cargo Concentration",
        conditions=[RuleCondition("top_berth_cargo_ratio", ">=", 0.6)],
        message_template="액체화물 처리량의 {top_berth_cargo_pct}%가 상위 부두에 집중되어 있습니다. 물동량 분산을 검토하십시오.",
        severity="info",
        related_entity_type="LiquidCargoStat",
    ),
]
