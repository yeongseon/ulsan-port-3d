import uuid
from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class PortZone(Base):
    __tablename__ = "port_zone"

    zone_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100))
    zone_type: Mapped[str] = mapped_column(String(50))
    geometry: Mapped[str | None] = mapped_column(Geometry("POLYGON", srid=4326), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    berths: Mapped[list["Berth"]] = relationship(back_populates="zone")
    buoys: Mapped[list["Buoy"]] = relationship(back_populates="zone")


class Berth(Base):
    __tablename__ = "berth"

    berth_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    facility_code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    zone_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("port_zone.zone_id"))
    operator_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("operator.operator_id"), nullable=True
    )
    length: Mapped[float | None] = mapped_column(Float, nullable=True)
    depth: Mapped[float | None] = mapped_column(Float, nullable=True)
    geometry: Mapped[str | None] = mapped_column(Geometry("POINT", srid=4326), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    zone: Mapped["PortZone"] = relationship(back_populates="berths")
    operator: Mapped["Operator | None"] = relationship(back_populates="berths")


class Buoy(Base):
    __tablename__ = "buoy"

    buoy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100))
    zone_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("port_zone.zone_id"))
    geometry: Mapped[str | None] = mapped_column(Geometry("POINT", srid=4326), nullable=True)

    zone: Mapped["PortZone"] = relationship(back_populates="buoys")


class Terminal(Base):
    __tablename__ = "terminal"

    terminal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(200))
    terminal_type: Mapped[str] = mapped_column(String(50))
    zone_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("port_zone.zone_id"))
    operator_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("operator.operator_id"), nullable=True
    )


class TankTerminal(Base):
    __tablename__ = "tank_terminal"

    tank_terminal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(200))
    zone_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("port_zone.zone_id"))
    operator_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("operator.operator_id"), nullable=True
    )
    capacity_kl: Mapped[float | None] = mapped_column(Float, nullable=True)
    tank_count: Mapped[int | None] = mapped_column(Integer, nullable=True)


class RouteSegment(Base):
    __tablename__ = "route_segment"

    segment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(200))
    zone_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("port_zone.zone_id"))
    geometry: Mapped[str | None] = mapped_column(Geometry("LINESTRING", srid=4326), nullable=True)
    width: Mapped[float | None] = mapped_column(Float, nullable=True)
    direction: Mapped[str | None] = mapped_column(String(50), nullable=True)


class Operator(Base):
    __tablename__ = "operator"

    operator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(200))
    operator_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    contact: Mapped[str | None] = mapped_column(String(200), nullable=True)

    berths: Mapped[list["Berth"]] = relationship(back_populates="operator")


class CargoType(Base):
    __tablename__ = "cargo_type"

    cargo_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(200), unique=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
