from content.storage_engine import ContentStore
from nlp.pipeline import NLPPipeline
from nlp.processors.entity_extractor import EntityExtractor
from content.fetcher import WebFetcher
from content.storage_engine import ContentStore
import asyncio
from loguru import logger
import json

if __name__ == "__main__":
    fetcher = WebFetcher()
    store = ContentStore()

    url = "https://en.wikipedia.org/wiki/Mitski"

    try:
        content = asyncio.run(fetcher.fetch(url))
        content_id = store.store_content(content)
    except Exception as e:
        logger.error(e)

    uid = "5682dfa9-18a8-4af3-ab39-fe20728b2bf9"

    store = ContentStore()
    record = store.get_content(uid)
    content = json.loads(record["content"])
    record["text"] = content["raw_text"]
    pipeline = NLPPipeline([EntityExtractor(model="en_core_web_lg")])
    results = pipeline.process(record["text"])
    print(record)
