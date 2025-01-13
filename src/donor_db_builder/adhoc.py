# from models.SQLModels import Individual, Organization, Location, Payment, Filer
# from donor_db_builder.database.sql import SQLHandler
# from donor_db_builder.ingest.campaign_finance import CampaignFinanceIngestor
from donor_db_builder.ingest.neontology import NeontologyIngestor
from donor_db_builder.config import get_project_paths
from neontology import init_neontology
from neontology.graphengines import Neo4jConfig

"""Ad-hoc script for development. Will be removed."""


def main():
    project_paths = get_project_paths()
    DATA_DIR = project_paths.get_path("data")
    DB_PATH = DATA_DIR / "app.db"

    # db_path = DB_PATH
    # sql = SQLHandler(
    #     db_path, [Individual, Organization, Location, Payment, Filer], echo=True
    # )
    # sql = SQLHandler(
    #     models=[Individual, Organization, Location, Payment, Filer], echo=True
    # )
    # ingestor = CampaignFinanceIngestor(sql, DATA_DIR)
    # ingestor.ingest()

    config = Neo4jConfig(
        uri="bolt://localhost:7687",  # OR use NEO4J_URI environment variable
        username="neo4j",  # OR use NEO4J_USERNAME environment variable
        password="donor-db-builder",  # OR use NEO4J_PASSWORD environment variable
    )

    ingestor = NeontologyIngestor(config, DATA_DIR)
    ingestor.ingest()


if __name__ == "__main__":
    main()
