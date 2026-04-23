from collections.abc import Mapping
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import httpx

from .config import etl_settings

logger = logging.getLogger(__name__)


def get_http_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        timeout=etl_settings.request_timeout,
        follow_redirects=True,
    )


async def fetch_with_retry(
    client: httpx.AsyncClient,
    url: str,
    params: Mapping[str, str | int | float | bool] | None = None,
    max_retries: int | None = None,
) -> httpx.Response:
    retries = max_retries if max_retries is not None else etl_settings.max_retries
    last_error: Exception | None = None

    for attempt in range(retries):
        try:
            response = await client.get(url, params=params)
            _ = response.raise_for_status()
            return response
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            last_error = e
            wait: int = 2**attempt
            logger.warning(
                f"Attempt {attempt + 1}/{retries} failed for {url}: {e}. Retrying in {wait}s"
            )
            import asyncio

            await asyncio.sleep(wait)

    raise last_error or RuntimeError(f"Failed to fetch {url}")


def save_raw_snapshot(source: str, data: dict[str, object] | list[object] | str) -> Path:
    now = datetime.now(timezone.utc)
    dir_path = Path(etl_settings.raw_data_dir) / source / now.strftime("%Y-%m-%d")
    dir_path.mkdir(parents=True, exist_ok=True)
    file_path = dir_path / f"{now.strftime('%H%M%S')}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        if isinstance(data, str):
            _ = f.write(data)
        else:
            json.dump(data, f, ensure_ascii=False, indent=2)

    logger.info(f"Saved raw snapshot: {file_path}")
    return file_path
