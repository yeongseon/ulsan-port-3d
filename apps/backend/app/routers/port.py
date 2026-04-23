from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.common import ProblemDetail
from app.schemas.port import PortOverviewResponse, ZoneResponse
from app.services import port as port_service

router = APIRouter(tags=["port"])


@router.get(
    "/port/overview",
    response_model=PortOverviewResponse,
    responses={500: {"model": ProblemDetail}},
)
async def get_port_overview(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PortOverviewResponse:
    return await port_service.get_port_overview(db)


@router.get(
    "/zones",
    response_model=list[ZoneResponse],
    responses={500: {"model": ProblemDetail}},
)
async def get_zones(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[ZoneResponse]:
    return await port_service.get_zones(db)
