# from content.storage_engine import ContentStore
# from nlp.pipeline import NLPPipeline
# from nlp.processors.entity_extractor import EntityExtractor
# from content.fetcher import WebFetcher
# from content.storage_engine import ContentStore
# import asyncio
# from loguru import logger
# import json
# from relik import Relik
# from relik.inference.data.objects import RelikOutput
# from llama_index.llms.openai import OpenAI
# from content.models_orm import WebContent
from models.SQLModels import Individual, Organization, Location, Payment, Filer
from pathlib import Path
from sqlmodel import create_engine, SQLModel
from donor_db_builder.database.sql import SQLHandler
from donor_db_builder.ingest.campaign_finance import CampaignFinanceIngestor
from donor_db_builder.config import get_settings, get_project_paths


def main():
    # fetcher = WebFetcher()
    # store = ContentStore()
    #
    # url = "https://en.wikipedia.org/wiki/Mitski"
    #
    # try:
    #     content = asyncio.run(fetcher.fetch(url))
    #     content_id = store.store_content(content)
    # except Exception as e:
    #     logger.error(e)
    #
    # uid = "5682dfa9-18a8-4af3-ab39-fe20728b2bf9"
    #
    # store = ContentStore()
    # record = store.get_content(uid)
    # content = json.loads(record["content"])
    # record["text"] = content["raw_text"]
    # pipeline = NLPPipeline([EntityExtractor(model="en_core_web_lg")])
    # results = pipeline.process(record["text"])
    # print(record)
    #
    # llm = OpenAI(model="gpt-4o")
    # sllm = llm.as_structured_llm()
    #
    # response = sllm.

    project_paths = get_project_paths()
    DATA_DIR = project_paths.get_path("data")
    DB_PATH = DATA_DIR / "app.db"

    db_path = DB_PATH
    sql = SQLHandler(
        db_path, [Individual, Organization, Location, Payment, Filer], echo=True
    )
    ingestor = CampaignFinanceIngestor(sql, DATA_DIR)
    ingestor.ingest()
    # engine = create_engine(f"duckdb:///{db_path}", echo=True)
    #
    # # self.conn = duckdb.connect(database=db_path)
    # SQLModel.metadata.create_all(engine)
    print("")


if __name__ == "__main__":
    main()
