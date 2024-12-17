from importer import DonorGraph
from socrata import SocrataHandler
from src.donor_db_builder.utils.logger import Logger
from dotenv import dotenv_values
import pandas as pd
import sys

config = dotenv_values(".env")

if __name__ == "__main__":
    Logger.setup_logger(app_name='donor_db_builder')
    logger = Logger.get_logger()
    logger.info("Starting Donor DB Builder")

    socrata = SocrataHandler(api_key=config["SOCRATA_API_KEY"])
    column_map = socrata.load_column_map(column_map_path="../data/cf_column_map.json")
    socrata.fetch_data(resource_id="e9ss-239a", date_from='2024-09-01', column_map=column_map, output_path="../data/cf_data.csv")


    try:

        uri = f"neo4j://{config['NEO_HOST']}:{config['NEO_PORT']}"
        username = config['NEO_USER']
        password = config['NEO_PASS']


        contributions_df = pd.read_csv("../data/cf_data.csv")
        filers_df = pd.read_csv("../data/cf_filers.csv")

        filer_limit = 200
        contribution_limit = 5000

        if filer_limit:
            filers_df = filers_df.head(filer_limit)

        if contribution_limit:
            contributions_df = contributions_df.head(contribution_limit)

        graph = DonorGraph(uri, username, password)
        graph.clear_database()
        graph.import_data(contributions_df, filers_df)
        graph.close()
    except Exception as e:
        logger.exception("Program failed")
        sys.exit(1)