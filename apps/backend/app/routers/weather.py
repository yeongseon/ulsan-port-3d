from fastapi import APIRouter

router = APIRouter(tags=["weather"])


@router.get("/weather/current")
async def get_weather_current() -> dict:
    return {}


@router.get("/weather/forecast")
async def get_weather_forecast(zone: str | None = None) -> list:
    return []
