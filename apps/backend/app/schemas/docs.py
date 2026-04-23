from app.schemas.common import APIModel


class HazardDocResponse(APIModel):
    doc_id: str
    title: str
    source_page: str | None
    published_date: str | None
    file_url: str | None
    related_cargo_type: str | None
    created_at: str | None


class MsdsDocResponse(APIModel):
    doc_id: str
    title: str
    cargo_type: str | None
    source_page: str | None
    file_url: str | None
    created_at: str | None


class SafetyManualDocResponse(APIModel):
    doc_id: str
    title: str
    source_page: str | None
    file_url: str | None
    created_at: str | None
