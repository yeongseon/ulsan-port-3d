from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.alert_engine import evaluate_alerts
from app.services.llm_summary import generate_llm_summary
from app.services.rule_engine import evaluate_rules, generate_current_insights

router = APIRouter(tags=["insights"])


@router.get("/insights/current")
async def get_current_insights(session: AsyncSession = Depends(get_db)) -> dict:
    insights = await generate_current_insights(session)

    context = {}
    if insights:
        context = insights[0].get("source_data", {})

    llm_summary = await generate_llm_summary(context) if context else None

    return {
        "rule_based_insights": insights,
        "llm_summary": llm_summary,
        "insight_count": len(insights),
    }


@router.get("/alerts")
async def get_alerts(session: AsyncSession = Depends(get_db)) -> dict:
    from sqlalchemy import select

    from app.models.documents import Alert

    result = await session.execute(
        select(Alert).where(Alert.is_active.is_(True)).order_by(Alert.created_at.desc()).limit(50)
    )
    alerts = result.scalars().all()

    return {
        "alerts": [
            {
                "alert_id": str(a.alert_id),
                "type": a.alert_type,
                "severity": a.severity,
                "message": a.message,
                "related_entity_type": a.related_entity_type,
                "related_entity_id": a.related_entity_id,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in alerts
        ],
        "total": len(alerts),
    }


@router.post("/alerts/evaluate")
async def trigger_alert_evaluation(session: AsyncSession = Depends(get_db)) -> dict:
    new_alerts = await evaluate_alerts(session)
    return {
        "new_alerts": new_alerts,
        "count": len(new_alerts),
    }
