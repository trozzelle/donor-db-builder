from dlt.sources.sql_database import sql_database

from models.SQLModels import Individual, Organization, Location, Payment, Filer
from donor_db_builder.database.sql import SQLHandler

# from donor_db_builder.ingest.campaign_finance import CampaignFinanceIngestor
from donor_db_builder.config import get_project_paths
from donor_db_builder.rag.openai import OpenAIRAG
from llama_index.core import SQLDatabase
from sqlalchemy import create_engine

"""Ad-hoc script for development. Will be removed."""


def main():
    project_paths = get_project_paths()
    DATA_DIR = project_paths.get_path("data")
    DB_PATH = DATA_DIR / "app.db"

    db_path = DB_PATH
    sql = SQLHandler(
        db_path, [Individual, Organization, Location, Payment, Filer], echo=True
    )
    # sql = SQLHandler(
    #     models=[Individual, Organization, Location, Payment, Filer], echo=True
    # )
    # ingestor = CampaignFinanceIngestor(sql, DATA_DIR)
    # ingestor.ingest()
    sql_db = SQLDatabase(sql.engine)
    rag = OpenAIRAG(
        database=sql_db,
        tables=["individual", "organization", "location", "payment", "filer"],
    )

    rag.setup_query_engine()

    response = rag.query("How many different cities do the donors live in?")
    print(response)


if __name__ == "__main__":
    main()
