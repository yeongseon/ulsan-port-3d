from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.timeseries import TideObservation, WeatherObservation
from app.schemas.weather import (
    TideObservationResponse,
    WeatherCurrentResponse,
    WeatherForecastResponse,
    WeatherObservationResponse,
)
from app.services.common import to_utc_iso


def _map_weather(observation: WeatherObservation) -> WeatherObservationResponse:
    return WeatherObservationResponse(
        zone_name=observation.zone_name,
        wind_speed=observation.wind_speed,
        wind_dir=observation.wind_dir,
        temperature=observation.temperature,
        humidity=observation.humidity,
        pressure=observation.pressure,
        precipitation=observation.precipitation,
        visibility=observation.visibility,
        wave_height=observation.wave_height,
        observed_at=to_utc_iso(observation.observed_at) or "",
    )


def _map_tide(observation: TideObservation) -> TideObservationResponse:
    return TideObservationResponse(
        station_name=observation.station_name,
        tide_level=observation.tide_level,
        observed_at=to_utc_iso(observation.observed_at) or "",
    )


async def get_weather_current(db: AsyncSession) -> WeatherCurrentResponse:
    weather_stmt = (
        select(WeatherObservation).order_by(WeatherObservation.observed_at.desc()).limit(1)
    )
    tide_stmt = select(TideObservation).order_by(TideObservation.observed_at.desc()).limit(1)
    weather = await db.scalar(weather_stmt)
    tide = await db.scalar(tide_stmt)
    return WeatherCurrentResponse(
        observation=_map_weather(weather) if weather is not None else None,
        tide=_map_tide(tide) if tide is not None else None,
    )


async def get_weather_forecast(
    db: AsyncSession, *, zone: str | None
) -> list[WeatherForecastResponse]:
    stmt = select(WeatherObservation)
    if zone:
        stmt = stmt.where(WeatherObservation.zone_name == zone)
    stmt = stmt.order_by(WeatherObservation.observed_at.desc()).limit(24)
    observations = (await db.scalars(stmt)).all()
    if zone:
        return [
            WeatherForecastResponse(
                zone_name=zone,
                observations=[_map_weather(observation) for observation in observations],
            )
        ]

    grouped: dict[str | None, list[WeatherObservationResponse]] = {}
    for observation in observations:
        grouped.setdefault(observation.zone_name, []).append(_map_weather(observation))
    return [
        WeatherForecastResponse(zone_name=zone_name, observations=items)
        for zone_name, items in grouped.items()
    ]
