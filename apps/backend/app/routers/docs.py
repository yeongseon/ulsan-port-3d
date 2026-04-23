from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.common import ProblemDetail
from app.schemas.docs import HazardDocResponse, MsdsDocResponse
from app.services import docs as docs_service

router = APIRouter(tags=["docs"])


@router.get(
    "/docs/hazard",
    response_model=list[HazardDocResponse],
    responses={500: {"model": ProblemDetail}},
)
async def get_hazard_docs(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[HazardDocResponse]:
    return await docs_service.get_hazard_docs(db)


@router.get(
    "/docs/msds",
    response_model=list[MsdsDocResponse],
    responses={500: {"model": ProblemDetail}},
)
async def get_msds_docs(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[MsdsDocResponse]:
    return await docs_service.get_msds_docs(db)
