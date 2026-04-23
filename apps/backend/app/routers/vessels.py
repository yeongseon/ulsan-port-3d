from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.common import ProblemDetail
from app.schemas.vessel import VesselDetailResponse, VesselLiveResponse
from app.services import vessels as vessel_service

router = APIRouter(tags=["vessels"])


@router.get(
    "/vessels",
    response_model=list[VesselLiveResponse],
    responses={500: {"model": ProblemDetail}},
)
async def get_vessels(
    zone: str | None = None,
    ship_type: str | None = None,
    *,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[VesselLiveResponse]:
    return await vessel_service.get_live_vessels(db, zone=zone, ship_type=ship_type)


@router.get(
    "/vessels/live",
    response_model=list[VesselLiveResponse],
    responses={500: {"model": ProblemDetail}},
)
async def get_vessels_live(
    zone: str | None = None,
    ship_type: str | None = None,
    *,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[VesselLiveResponse]:
    return await vessel_service.get_live_vessels(db, zone=zone, ship_type=ship_type)


@router.get(
    "/vessels/{vessel_id}",
    response_model=VesselDetailResponse,
    responses={404: {"model": ProblemDetail}, 500: {"model": ProblemDetail}},
)
async def get_vessel_detail(
    vessel_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> VesselDetailResponse:
    return await vessel_service.get_vessel_detail(db, vessel_id)
