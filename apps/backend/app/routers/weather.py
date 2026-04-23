from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.common import ProblemDetail
from app.schemas.weather import WeatherCurrentResponse, WeatherForecastResponse
from app.services import weather as weather_service

router = APIRouter(tags=["weather"])


@router.get(
    "/weather/current",
    response_model=WeatherCurrentResponse,
    responses={500: {"model": ProblemDetail}},
)
async def get_weather_current(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> WeatherCurrentResponse:
    return await weather_service.get_weather_current(db)


@router.get(
    "/weather/forecast",
    response_model=list[WeatherForecastResponse],
    responses={500: {"model": ProblemDetail}},
)
async def get_weather_forecast(
    zone: str | None = None,
    *,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[WeatherForecastResponse]:
    return await weather_service.get_weather_forecast(db, zone=zone)
