from typing import Optional, Dict, Any
import httpx
import trafilatura
from datetime import datetime, timezone
from loguru import logger
from urllib.parse import urlparse
import json


class WebFetcher:
    """Retrieves and extracts content from web pages"""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    async def fetch(self, url: str) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()

                extracted = trafilatura.extract(
                    response.text,
                    include_comments=False,
                    include_tables=True,
                    output_format="json",
                    with_metadata=True,
                )

                if not extracted:
                    raise ValueError(
                        "No content could be extracted from the provided URL"
                    )

                return {
                    "url": url,
                    "domain": urlparse(url).netloc,
                    "fetched_at": datetime.now(timezone.utc),
                    "content": extracted,
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                }

        except Exception as e:
            logger.error(f"Failed to fetch content from {url}: {str(e)}")
            raise
