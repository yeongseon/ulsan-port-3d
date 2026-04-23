import uuid
from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class VesselPosition(Base):
    __tablename__ = "vessel_position"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vessel_id: Mapped[str] = mapped_column(String(100), index=True)
    name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    call_sign: Mapped[str | None] = mapped_column(String(50), nullable=True)
    imo: Mapped[str | None] = mapped_column(String(20), nullable=True)
    ship_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    gross_tonnage: Mapped[float | None] = mapped_column(Float, nullable=True)
    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)
    speed: Mapped[float | None] = mapped_column(Float, nullable=True)
    course: Mapped[float | None] = mapped_column(Float, nullable=True)
    heading: Mapped[float | None] = mapped_column(Float, nullable=True)
    draft: Mapped[float | None] = mapped_column(Float, nullable=True)
    geometry: Mapped[str | None] = mapped_column(Geometry("POINT", srid=4326), nullable=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class LatestVesselPosition(Base):
    __tablename__ = "latest_vessel_position"

    vessel_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    call_sign: Mapped[str | None] = mapped_column(String(50), nullable=True)
    imo: Mapped[str | None] = mapped_column(String(20), nullable=True)
    ship_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    gross_tonnage: Mapped[float | None] = mapped_column(Float, nullable=True)
    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)
    speed: Mapped[float | None] = mapped_column(Float, nullable=True)
    course: Mapped[float | None] = mapped_column(Float, nullable=True)
    heading: Mapped[float | None] = mapped_column(Float, nullable=True)
    draft: Mapped[float | None] = mapped_column(Float, nullable=True)
    geometry: Mapped[str | None] = mapped_column(Geometry("POINT", srid=4326), nullable=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class VesselEvent(Base):
    __tablename__ = "vessel_event"

    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    vessel_id: Mapped[str] = mapped_column(String(100), index=True)
    call_sign: Mapped[str | None] = mapped_column(String(50), nullable=True)
    event_type: Mapped[str] = mapped_column(String(50))
    berth_facility_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class BerthStatus(Base):
    __tablename__ = "berth_status"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    berth_facility_code: Mapped[str] = mapped_column(
        String(50), ForeignKey("berth.facility_code"), index=True
    )
    status: Mapped[str] = mapped_column(String(50))
    status_detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class LatestBerthStatus(Base):
    __tablename__ = "latest_berth_status"

    berth_facility_code: Mapped[str] = mapped_column(String(50), primary_key=True)
    berth_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    zone_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(50))
    status_detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class WeatherObservation(Base):
    __tablename__ = "weather_observation"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    zone_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    wind_speed: Mapped[float | None] = mapped_column(Float, nullable=True)
    wind_dir: Mapped[float | None] = mapped_column(Float, nullable=True)
    temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    humidity: Mapped[float | None] = mapped_column(Float, nullable=True)
    pressure: Mapped[float | None] = mapped_column(Float, nullable=True)
    precipitation: Mapped[float | None] = mapped_column(Float, nullable=True)
    visibility: Mapped[float | None] = mapped_column(Float, nullable=True)
    wave_height: Mapped[float | None] = mapped_column(Float, nullable=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class TideObservation(Base):
    __tablename__ = "tide_observation"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    station_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tide_level: Mapped[float | None] = mapped_column(Float, nullable=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CargoStatMonthly(Base):
    __tablename__ = "cargo_stat_monthly"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    year_month: Mapped[str] = mapped_column(String(7), index=True)
    zone_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    berth_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    cargo_type: Mapped[str | None] = mapped_column(String(200), nullable=True)
    volume_ton: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ArrivalStatMonthly(Base):
    __tablename__ = "arrival_stat_monthly"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    year_month: Mapped[str] = mapped_column(String(7), index=True)
    zone_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    berth_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    vessel_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CongestionStat(Base):
    __tablename__ = "congestion_stat"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stat_date: Mapped[str] = mapped_column(String(10), index=True)
    waiting_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    avg_wait_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
