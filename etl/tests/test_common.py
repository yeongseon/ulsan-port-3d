from pathlib import Path

import httpx
import pytest

from ..common import fetch_with_retry, get_http_client, save_raw_snapshot
from ..config import etl_settings


def test_get_http_client_uses_etl_settings() -> None:
    client = get_http_client()

    assert client.follow_redirects is True
    assert client.timeout.connect == etl_settings.request_timeout


@pytest.mark.asyncio
async def test_fetch_with_retry_retries_then_succeeds() -> None:
    attempts = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        attempts["count"] += 1
        if attempts["count"] == 1:
            return httpx.Response(503, request=request)
        return httpx.Response(200, request=request, json={"ok": True})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        response: httpx.Response = await fetch_with_retry(
            client, "https://example.test", max_retries=2
        )

    assert attempts["count"] == 2
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_save_raw_snapshot_writes_json_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(etl_settings, "raw_data_dir", str(tmp_path))

    file_path = save_raw_snapshot("unit-test-source", {"value": 1})

    assert file_path.exists()
    assert file_path.suffix == ".json"
    assert "unit-test-source" in str(file_path)
    assert file_path.read_text(encoding="utf-8").strip().startswith("{")
