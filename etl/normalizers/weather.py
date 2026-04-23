from typing import Any, TypedDict

from .common import clean_string, extract_zone_name, to_float


class WeatherObservationRecord(TypedDict):
    zone_name: str | None
    wind_speed: float | None
    wind_dir: float | None
    temperature: float | None
    humidity: float | None
    pressure: float | None
    precipitation: float | None
    visibility: float | None
    wave_height: float | None


class TideObservationRecord(TypedDict):
    station_name: str | None
    tide_level: float | None


def normalize_weather_items(items: list[dict[str, Any]]) -> list[WeatherObservationRecord]:
    normalized: list[WeatherObservationRecord] = []
    for item in items:
        normalized.append(
            {
                "zone_name": extract_zone_name(item),
                "wind_speed": to_float(item.get("windSpeed")),
                "wind_dir": to_float(item.get("windDir")),
                "temperature": to_float(item.get("temperature")),
                "humidity": to_float(item.get("humidity")),
                "pressure": to_float(item.get("pressure")),
                "precipitation": to_float(item.get("precipitation")),
                "visibility": to_float(item.get("visibility")),
                "wave_height": to_float(item.get("waveHeight")),
            }
        )
    return normalized


def normalize_tide_items(items: list[dict[str, Any]]) -> list[TideObservationRecord]:
    normalized: list[TideObservationRecord] = []
    for item in items:
        normalized.append(
            {
                "station_name": clean_string(item.get("stationName")),
                "tide_level": to_float(item.get("tideLevel")),
            }
        )
    return normalized
