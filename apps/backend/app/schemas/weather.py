from app.schemas.common import APIModel


class TideObservationResponse(APIModel):
    station_name: str | None
    tide_level: float | None
    observed_at: str


class WeatherObservationResponse(APIModel):
    zone_name: str | None
    wind_speed: float | None
    wind_dir: float | None
    temperature: float | None
    humidity: float | None
    pressure: float | None
    precipitation: float | None
    visibility: float | None
    wave_height: float | None
    observed_at: str


class WeatherCurrentResponse(APIModel):
    observation: WeatherObservationResponse | None
    tide: TideObservationResponse | None


class WeatherForecastResponse(APIModel):
    zone_name: str | None
    observations: list[WeatherObservationResponse]
