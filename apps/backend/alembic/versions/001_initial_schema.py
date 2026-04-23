from collections.abc import Sequence

from alembic import op
import geoalchemy2
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.create_table(
        "alert",
        sa.Column("alert_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("alert_type", sa.String(length=50), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("related_entity_type", sa.String(length=50), nullable=True),
        sa.Column("related_entity_id", sa.String(length=100), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("alert_id", name=op.f("pk_alert")),
    )
    op.create_table(
        "cargo_type",
        sa.Column("cargo_type_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint("cargo_type_id", name=op.f("pk_cargo_type")),
        sa.UniqueConstraint("name", name=op.f("uq_cargo_type_name")),
    )
    op.create_table(
        "congestion_stat",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("stat_date", sa.String(length=10), nullable=False),
        sa.Column("waiting_count", sa.Integer(), nullable=True),
        sa.Column("avg_wait_hours", sa.Float(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_congestion_stat")),
    )
    op.create_index(
        op.f("ix_congestion_stat_stat_date"), "congestion_stat", ["stat_date"], unique=False
    )
    op.create_table(
        "daily_port_snapshot",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("snapshot_date", sa.String(length=10), nullable=False),
        sa.Column("active_vessel_count", sa.Integer(), nullable=True),
        sa.Column("berth_utilization", sa.Float(), nullable=True),
        sa.Column("alert_count", sa.Integer(), nullable=True),
        sa.Column("summary_data", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_daily_port_snapshot")),
        sa.UniqueConstraint("snapshot_date", name=op.f("uq_daily_port_snapshot_snapshot_date")),
    )
    op.create_index(
        op.f("ix_daily_port_snapshot_snapshot_date"),
        "daily_port_snapshot",
        ["snapshot_date"],
        unique=False,
    )
    op.create_table(
        "hazard_doc",
        sa.Column("doc_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("source_page", sa.String(length=500), nullable=True),
        sa.Column("published_date", sa.String(length=20), nullable=True),
        sa.Column("file_url", sa.String(length=1000), nullable=True),
        sa.Column("related_cargo_type", sa.String(length=200), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("doc_id", name=op.f("pk_hazard_doc")),
    )
    op.create_table(
        "insight",
        sa.Column("insight_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("insight_type", sa.String(length=50), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("source_data", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("insight_id", name=op.f("pk_insight")),
    )
    op.create_table(
        "latest_vessel_position",
        sa.Column("vessel_id", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=True),
        sa.Column("call_sign", sa.String(length=50), nullable=True),
        sa.Column("imo", sa.String(length=20), nullable=True),
        sa.Column("ship_type", sa.String(length=50), nullable=True),
        sa.Column("gross_tonnage", sa.Float(), nullable=True),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lon", sa.Float(), nullable=False),
        sa.Column("speed", sa.Float(), nullable=True),
        sa.Column("course", sa.Float(), nullable=True),
        sa.Column("heading", sa.Float(), nullable=True),
        sa.Column("draft", sa.Float(), nullable=True),
        sa.Column(
            "geometry", geoalchemy2.Geometry(geometry_type="POINT", srid=4326), nullable=True
        ),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("vessel_id", name=op.f("pk_latest_vessel_position")),
    )
    op.create_table(
        "msds_doc",
        sa.Column("doc_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("cargo_type", sa.String(length=200), nullable=True),
        sa.Column("source_page", sa.String(length=500), nullable=True),
        sa.Column("file_url", sa.String(length=1000), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("doc_id", name=op.f("pk_msds_doc")),
    )
    op.create_table(
        "operator",
        sa.Column("operator_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("operator_type", sa.String(length=50), nullable=True),
        sa.Column("contact", sa.String(length=200), nullable=True),
        sa.PrimaryKeyConstraint("operator_id", name=op.f("pk_operator")),
    )
    op.create_table(
        "port_zone",
        sa.Column("zone_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("zone_type", sa.String(length=50), nullable=False),
        sa.Column(
            "geometry", geoalchemy2.Geometry(geometry_type="POLYGON", srid=4326), nullable=True
        ),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("zone_id", name=op.f("pk_port_zone")),
    )
    op.create_table(
        "safety_manual_doc",
        sa.Column("doc_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("source_page", sa.String(length=500), nullable=True),
        sa.Column("file_url", sa.String(length=1000), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("doc_id", name=op.f("pk_safety_manual_doc")),
    )
    op.create_table(
        "scenario_demo_frame",
        sa.Column("frame_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("scenario_id", sa.String(length=100), nullable=False),
        sa.Column("frame_index", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.String(length=30), nullable=False),
        sa.Column("vessel_positions", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("berth_statuses", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("weather", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("alerts", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("ai_summary", sa.Text(), nullable=True),
        sa.Column("is_simulated", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("frame_id", name=op.f("pk_scenario_demo_frame")),
    )
    op.create_index(
        op.f("ix_scenario_demo_frame_scenario_id"),
        "scenario_demo_frame",
        ["scenario_id"],
        unique=False,
    )
    op.create_table(
        "tide_observation",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("station_name", sa.String(length=100), nullable=True),
        sa.Column("tide_level", sa.Float(), nullable=True),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tide_observation")),
    )
    op.create_index(
        op.f("ix_tide_observation_observed_at"), "tide_observation", ["observed_at"], unique=False
    )
    op.create_table(
        "vessel_event",
        sa.Column("event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("vessel_id", sa.String(length=100), nullable=False),
        sa.Column("call_sign", sa.String(length=50), nullable=True),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("berth_facility_code", sa.String(length=50), nullable=True),
        sa.Column("event_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("detail", sa.Text(), nullable=True),
        sa.Column("raw_data", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("event_id", name=op.f("pk_vessel_event")),
    )
    op.create_index(
        op.f("ix_vessel_event_event_time"), "vessel_event", ["event_time"], unique=False
    )
    op.create_index(op.f("ix_vessel_event_vessel_id"), "vessel_event", ["vessel_id"], unique=False)
    op.create_table(
        "vessel_position",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("vessel_id", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=True),
        sa.Column("call_sign", sa.String(length=50), nullable=True),
        sa.Column("imo", sa.String(length=20), nullable=True),
        sa.Column("ship_type", sa.String(length=50), nullable=True),
        sa.Column("gross_tonnage", sa.Float(), nullable=True),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lon", sa.Float(), nullable=False),
        sa.Column("speed", sa.Float(), nullable=True),
        sa.Column("course", sa.Float(), nullable=True),
        sa.Column("heading", sa.Float(), nullable=True),
        sa.Column("draft", sa.Float(), nullable=True),
        sa.Column(
            "geometry", geoalchemy2.Geometry(geometry_type="POINT", srid=4326), nullable=True
        ),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_vessel_position")),
    )
    op.create_index(
        op.f("ix_vessel_position_observed_at"), "vessel_position", ["observed_at"], unique=False
    )
    op.create_index(
        op.f("ix_vessel_position_vessel_id"), "vessel_position", ["vessel_id"], unique=False
    )
    op.create_table(
        "weather_observation",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("zone_name", sa.String(length=100), nullable=True),
        sa.Column("wind_speed", sa.Float(), nullable=True),
        sa.Column("wind_dir", sa.Float(), nullable=True),
        sa.Column("temperature", sa.Float(), nullable=True),
        sa.Column("humidity", sa.Float(), nullable=True),
        sa.Column("pressure", sa.Float(), nullable=True),
        sa.Column("precipitation", sa.Float(), nullable=True),
        sa.Column("visibility", sa.Float(), nullable=True),
        sa.Column("wave_height", sa.Float(), nullable=True),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_weather_observation")),
    )
    op.create_index(
        op.f("ix_weather_observation_observed_at"),
        "weather_observation",
        ["observed_at"],
        unique=False,
    )
    op.create_table(
        "arrival_stat_monthly",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("year_month", sa.String(length=7), nullable=False),
        sa.Column("zone_name", sa.String(length=100), nullable=True),
        sa.Column("berth_name", sa.String(length=200), nullable=True),
        sa.Column("vessel_count", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_arrival_stat_monthly")),
    )
    op.create_index(
        op.f("ix_arrival_stat_monthly_year_month"),
        "arrival_stat_monthly",
        ["year_month"],
        unique=False,
    )
    op.create_table(
        "berth",
        sa.Column("berth_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("facility_code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("zone_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("operator_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("length", sa.Float(), nullable=True),
        sa.Column("depth", sa.Float(), nullable=True),
        sa.Column(
            "geometry", geoalchemy2.Geometry(geometry_type="POINT", srid=4326), nullable=True
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["operator_id"], ["operator.operator_id"], name=op.f("fk_berth_operator_id_operator")
        ),
        sa.ForeignKeyConstraint(
            ["zone_id"], ["port_zone.zone_id"], name=op.f("fk_berth_zone_id_port_zone")
        ),
        sa.PrimaryKeyConstraint("berth_id", name=op.f("pk_berth")),
        sa.UniqueConstraint("facility_code", name=op.f("uq_berth_facility_code")),
    )
    op.create_index(op.f("ix_berth_facility_code"), "berth", ["facility_code"], unique=True)
    op.create_table(
        "buoy",
        sa.Column("buoy_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("zone_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "geometry", geoalchemy2.Geometry(geometry_type="POINT", srid=4326), nullable=True
        ),
        sa.ForeignKeyConstraint(
            ["zone_id"], ["port_zone.zone_id"], name=op.f("fk_buoy_zone_id_port_zone")
        ),
        sa.PrimaryKeyConstraint("buoy_id", name=op.f("pk_buoy")),
    )
    op.create_table(
        "cargo_stat_monthly",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("year_month", sa.String(length=7), nullable=False),
        sa.Column("zone_name", sa.String(length=100), nullable=True),
        sa.Column("berth_name", sa.String(length=200), nullable=True),
        sa.Column("cargo_type", sa.String(length=200), nullable=True),
        sa.Column("volume_ton", sa.Float(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_cargo_stat_monthly")),
    )
    op.create_index(
        op.f("ix_cargo_stat_monthly_year_month"), "cargo_stat_monthly", ["year_month"], unique=False
    )
    op.create_table(
        "route_segment",
        sa.Column("segment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("zone_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "geometry", geoalchemy2.Geometry(geometry_type="LINESTRING", srid=4326), nullable=True
        ),
        sa.Column("width", sa.Float(), nullable=True),
        sa.Column("direction", sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(
            ["zone_id"], ["port_zone.zone_id"], name=op.f("fk_route_segment_zone_id_port_zone")
        ),
        sa.PrimaryKeyConstraint("segment_id", name=op.f("pk_route_segment")),
    )
    op.create_table(
        "tank_terminal",
        sa.Column("tank_terminal_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("zone_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("operator_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("capacity_kl", sa.Float(), nullable=True),
        sa.Column("tank_count", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["operator_id"],
            ["operator.operator_id"],
            name=op.f("fk_tank_terminal_operator_id_operator"),
        ),
        sa.ForeignKeyConstraint(
            ["zone_id"], ["port_zone.zone_id"], name=op.f("fk_tank_terminal_zone_id_port_zone")
        ),
        sa.PrimaryKeyConstraint("tank_terminal_id", name=op.f("pk_tank_terminal")),
    )
    op.create_table(
        "terminal",
        sa.Column("terminal_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("terminal_type", sa.String(length=50), nullable=False),
        sa.Column("zone_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("operator_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["operator_id"], ["operator.operator_id"], name=op.f("fk_terminal_operator_id_operator")
        ),
        sa.ForeignKeyConstraint(
            ["zone_id"], ["port_zone.zone_id"], name=op.f("fk_terminal_zone_id_port_zone")
        ),
        sa.PrimaryKeyConstraint("terminal_id", name=op.f("pk_terminal")),
    )
    op.create_table(
        "berth_status",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("berth_facility_code", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("status_detail", sa.Text(), nullable=True),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["berth_facility_code"],
            ["berth.facility_code"],
            name=op.f("fk_berth_status_berth_facility_code_berth"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_berth_status")),
    )
    op.create_index(
        op.f("ix_berth_status_berth_facility_code"),
        "berth_status",
        ["berth_facility_code"],
        unique=False,
    )
    op.create_index(
        op.f("ix_berth_status_observed_at"), "berth_status", ["observed_at"], unique=False
    )
    op.create_table(
        "latest_berth_status",
        sa.Column("berth_facility_code", sa.String(length=50), nullable=False),
        sa.Column("berth_name", sa.String(length=200), nullable=True),
        sa.Column("zone_name", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("status_detail", sa.Text(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("berth_facility_code", name=op.f("pk_latest_berth_status")),
    )


def downgrade() -> None:
    op.drop_table("latest_berth_status")
    op.drop_index(op.f("ix_berth_status_observed_at"), table_name="berth_status")
    op.drop_index(op.f("ix_berth_status_berth_facility_code"), table_name="berth_status")
    op.drop_table("berth_status")
    op.drop_table("terminal")
    op.drop_table("tank_terminal")
    op.drop_table("route_segment")
    op.drop_index(op.f("ix_cargo_stat_monthly_year_month"), table_name="cargo_stat_monthly")
    op.drop_table("cargo_stat_monthly")
    op.drop_table("buoy")
    op.drop_index(op.f("ix_berth_facility_code"), table_name="berth")
    op.drop_table("berth")
    op.drop_index(op.f("ix_arrival_stat_monthly_year_month"), table_name="arrival_stat_monthly")
    op.drop_table("arrival_stat_monthly")
    op.drop_index(op.f("ix_weather_observation_observed_at"), table_name="weather_observation")
    op.drop_table("weather_observation")
    op.drop_index(op.f("ix_vessel_position_vessel_id"), table_name="vessel_position")
    op.drop_index(op.f("ix_vessel_position_observed_at"), table_name="vessel_position")
    op.drop_table("vessel_position")
    op.drop_index(op.f("ix_vessel_event_vessel_id"), table_name="vessel_event")
    op.drop_index(op.f("ix_vessel_event_event_time"), table_name="vessel_event")
    op.drop_table("vessel_event")
    op.drop_index(op.f("ix_tide_observation_observed_at"), table_name="tide_observation")
    op.drop_table("tide_observation")
    op.drop_index(op.f("ix_scenario_demo_frame_scenario_id"), table_name="scenario_demo_frame")
    op.drop_table("scenario_demo_frame")
    op.drop_table("safety_manual_doc")
    op.drop_table("port_zone")
    op.drop_table("operator")
    op.drop_table("msds_doc")
    op.drop_table("latest_vessel_position")
    op.drop_table("insight")
    op.drop_table("hazard_doc")
    op.drop_index(op.f("ix_daily_port_snapshot_snapshot_date"), table_name="daily_port_snapshot")
    op.drop_table("daily_port_snapshot")
    op.drop_index(op.f("ix_congestion_stat_stat_date"), table_name="congestion_stat")
    op.drop_table("congestion_stat")
    op.drop_table("cargo_type")
    op.drop_table("alert")
