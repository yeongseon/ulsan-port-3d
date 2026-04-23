from datetime import datetime, timezone
from uuid import UUID

from app.core.errors import ProblemHTTPException


def to_utc_iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    normalized = value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
    return normalized.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def stringify_id(value: UUID | str | int) -> str:
    return str(value)


def parse_uuid_or_none(value: str) -> UUID | None:
    try:
        return UUID(value)
    except ValueError:
        return None


def not_found(detail: str) -> ProblemHTTPException:
    return ProblemHTTPException(status=404, title="Resource Not Found", detail=detail)
