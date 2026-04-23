from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.documents import HazardDoc, MsdsDoc
from app.schemas.docs import HazardDocResponse, MsdsDocResponse
from app.services.common import to_utc_iso


async def get_hazard_docs(db: AsyncSession) -> list[HazardDocResponse]:
    stmt = select(HazardDoc).order_by(desc(HazardDoc.published_date), HazardDoc.title.asc())
    items = (await db.scalars(stmt)).all()
    return [
        HazardDocResponse(
            doc_id=str(item.doc_id),
            title=item.title,
            source_page=item.source_page,
            published_date=item.published_date,
            file_url=item.file_url,
            related_cargo_type=item.related_cargo_type,
            created_at=to_utc_iso(item.created_at),
        )
        for item in items
    ]


async def get_msds_docs(db: AsyncSession) -> list[MsdsDocResponse]:
    stmt = select(MsdsDoc).order_by(MsdsDoc.cargo_type.asc(), MsdsDoc.title.asc())
    items = (await db.scalars(stmt)).all()
    return [
        MsdsDocResponse(
            doc_id=str(item.doc_id),
            title=item.title,
            cargo_type=item.cargo_type,
            source_page=item.source_page,
            file_url=item.file_url,
            created_at=to_utc_iso(item.created_at),
        )
        for item in items
    ]
