from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.documents import ScenarioDemoFrame
from app.schemas.scenarios import ScenarioFrameResponse, ScenarioSummaryResponse
from app.services.common import not_found, to_utc_iso


async def get_scenarios(db: AsyncSession) -> list[ScenarioSummaryResponse]:
    stmt = (
        select(
            ScenarioDemoFrame.scenario_id,
            func.count(ScenarioDemoFrame.frame_id),
            func.min(ScenarioDemoFrame.frame_index),
            func.max(ScenarioDemoFrame.frame_index),
            func.min(ScenarioDemoFrame.timestamp),
            func.max(ScenarioDemoFrame.timestamp),
            func.bool_or(ScenarioDemoFrame.is_simulated),
        )
        .group_by(ScenarioDemoFrame.scenario_id)
        .order_by(ScenarioDemoFrame.scenario_id.asc())
    )
    rows = (await db.execute(stmt)).all()
    return [
        ScenarioSummaryResponse(
            scenario_id=scenario_id,
            frame_count=frame_count,
            first_frame_index=first_frame_index,
            last_frame_index=last_frame_index,
            first_timestamp=first_timestamp,
            last_timestamp=last_timestamp,
            is_simulated=is_simulated,
        )
        for (
            scenario_id,
            frame_count,
            first_frame_index,
            last_frame_index,
            first_timestamp,
            last_timestamp,
            is_simulated,
        ) in rows
    ]


async def get_scenario_frames(db: AsyncSession, *, scenario_id: str) -> list[ScenarioFrameResponse]:
    stmt = (
        select(ScenarioDemoFrame)
        .where(ScenarioDemoFrame.scenario_id == scenario_id)
        .order_by(ScenarioDemoFrame.frame_index.asc())
    )
    items = (await db.scalars(stmt)).all()
    if not items:
        raise not_found(f"Scenario '{scenario_id}' was not found.")
    return [
        ScenarioFrameResponse(
            frame_id=str(item.frame_id),
            scenario_id=item.scenario_id,
            frame_index=item.frame_index,
            timestamp=item.timestamp,
            vessel_positions=item.vessel_positions,
            berth_statuses=item.berth_statuses,
            weather=item.weather,
            alerts=item.alerts,
            ai_summary=item.ai_summary,
            is_simulated=item.is_simulated,
            created_at=to_utc_iso(item.created_at),
        )
        for item in items
    ]
