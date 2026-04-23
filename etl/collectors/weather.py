import logging

from etl.common import fetch_with_retry, get_http_client, save_raw_snapshot
from etl.config import etl_settings
from etl.database import async_session
from etl.normalizers import extract_items, normalize_tide_items, normalize_weather_items

logger = logging.getLogger(__name__)

WEATHER_URL = f"{etl_settings.upa_api_base}/port/weather/current"
FORECAST_URL = f"{etl_settings.upa_api_base}/port/weather/forecast"
TIDE_URL = f"{etl_settings.upa_api_base}/port/tide/observation"


async def collect_weather() -> None:
    logger.info("Collecting weather data")
    try:
        async with get_http_client() as client:
            params = {"serviceKey": etl_settings.upa_api_key, "type": "json"}

            weather_resp = await fetch_with_retry(client, WEATHER_URL, params=params)
            weather_data = weather_resp.json()
            save_raw_snapshot("weather_current", weather_data)

            try:
                tide_resp = await fetch_with_retry(client, TIDE_URL, params=params)
                tide_data = tide_resp.json()
                save_raw_snapshot("tide_observation", tide_data)
            except Exception:
                logger.warning("Tide data collection failed, continuing without it")
                tide_data = {}

        async with async_session() as session:
            await _insert_weather(session, weather_data)
            if tide_data:
                await _insert_tide(session, tide_data)
            await session.commit()

        logger.info("Weather data collected successfully")
    except Exception:
        logger.exception("Failed to collect weather data")


async def _insert_weather(session, data: dict[str, object]) -> None:  # type: ignore[no-untyped-def]
    from sqlalchemy import text

    raw_items = extract_items(data)
    items = normalize_weather_items(raw_items)
    for item in items:
        await session.execute(
            text("""
                INSERT INTO weather_observation
                    (zone_name, wind_speed, wind_dir, temperature, humidity, pressure,
                     precipitation, visibility, wave_height, observed_at)
                VALUES
                    (:zone, :ws, :wd, :temp, :hum, :pres, :prec, :vis, :wave, NOW())
            """),
            {
                "zone": item.get("zone_name"),
                "ws": item.get("wind_speed"),
                "wd": item.get("wind_dir"),
                "temp": item.get("temperature"),
                "hum": item.get("humidity"),
                "pres": item.get("pressure"),
                "prec": item.get("precipitation"),
                "vis": item.get("visibility"),
                "wave": item.get("wave_height"),
            },
        )


async def _insert_tide(session, data: dict[str, object]) -> None:  # type: ignore[no-untyped-def]
    from sqlalchemy import text

    raw_items = extract_items(data)
    items = normalize_tide_items(raw_items)
    for item in items:
        await session.execute(
            text("""
                INSERT INTO tide_observation (station_name, tide_level, observed_at)
                VALUES (:station, :level, NOW())
            """),
            {
                "station": item.get("station_name"),
                "level": item.get("tide_level"),
            },
        )
