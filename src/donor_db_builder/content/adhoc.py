import asyncio
from fetcher import WebFetcher

# from storage import ContentStore
from storage_engine import ContentStore
from loguru import logger

if __name__ == "__main__":
    fetcher = WebFetcher()
    store = ContentStore()

    url = "https://en.wikipedia.org/wiki/Mitski"

    try:
        content = asyncio.run(fetcher.fetch(url))
        content_id = store.store_content(content)
    except Exception as e:
        logger.error(e)
