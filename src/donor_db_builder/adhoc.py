from models.SQLModels import Individual, Organization, Location, Payment, Filer
from donor_db_builder.database.sql import SQLHandler
from donor_db_builder.ingest.campaign_finance import CampaignFinanceIngestor
from donor_db_builder.config import get_project_paths

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
    ingestor = CampaignFinanceIngestor(sql, DATA_DIR)
    ingestor.ingest()


if __name__ == "__main__":
    main()
