import polars as pl
import requests
from io import StringIO
from typing import List, Optional

from requests.auth import HTTPBasicAuth

from src.donor_db_builder.utils.logger import Logger
import json
import os

logger = Logger.get_logger()

class SocrataHandler:
    """
    Handler for fetching data from Socrata API endpoints
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://data.ny.gov/resource"
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.auth = HTTPBasicAuth('EniidyLznn7X9znOLfwxzVO6L', '_gWCyCPQc8_ImipXqReP4d_WHRvN2EGKODFg')
        self.headers = {
            'Accept': 'text/csv',
            'X-APP-TOKEN': api_key
        }

    def load_column_map(self, column_map_path: str) -> List[str]:
        """Load default column names from JSON file"""
        try:
            with open(column_map_path, 'r') as f:
                column_map = json.load(f)
                self.column_map = column_map['columns']
                return column_map['columns']
        except Exception as e:
            logger.error(f"Failed to load default column map: {str(e)}")
            return []

    def fetch_data(
        self,
        resource_id: str,
        column_map: List[str] = None,
        date_from: Optional[str] = None,
        chunk_size: int = 1000000,
        output_path: Optional[str] = None
    ) -> pl.DataFrame:
        """
        Fetch data from Socrata API with pagination
        
        Args:
            resource_id: Socrata resource identifier
            column_map: List of column names to map to the CSV
            date_from: Optional date filter (format: YYYY-MM-DD)
            chunk_size: Number of records per request
            output_path: Optional path to save CSV output
            
        Returns:
            Polars DataFrame containing all fetched data
        """
        url = f"{self.base_url}/{resource_id}.csv?"
        offset = 0
        all_chunks = []

        # column_map = column_map if column_map else self.column_map

        try:
            while True:
                filters = {
                    '$select': ':*, *'
                }
                
                if date_from:
                    filters['$where'] = f"sched_date>'{date_from}'"

                params = {
                    '$limit': chunk_size,
                    '$offset': offset,
                    '$order': ':id',
                    **filters
                }

                logger.info(f"Requesting data set from Socrata API (offset: {offset})")
                response = requests.get(url, headers=self.headers, auth=self.auth, params=params)
                response.raise_for_status()

                if not response.content:
                    break

                logger.info("Reading CSV chunk")
                chunk_df = pl.read_csv(
                    StringIO(response.text),
                    encoding='utf-8',
                    infer_schema=False,
                    new_columns=column_map
                )

                if len(chunk_df) == 0:
                    break

                all_chunks.append(chunk_df)
                offset += chunk_size
                logger.info(f"Processed {offset} records")

            if not all_chunks:
                logger.warning("No data was fetched from the API")
                return pl.DataFrame()

            final_df = pl.concat(all_chunks)
            
            if output_path:
                logger.info(f"Writing data to {output_path}")
                final_df.write_csv(output_path)

        except Exception as e:
            logger.error(f"Error fetching data from Socrata: {str(e)}")
            raise

if __name__ == "__main__":
    print(os.getcwd())
    socrata = SocrataHandler("c16xa2cqxdop6q2rt7zx3t6ht", "https://data.ny.gov/resource")
    column_map = socrata.load_column_map('src/data/cf_column_map.json')
    socrata.fetch_data(resource_id='4j2b-6a2j', column_map=column_map, date_from='2024-01-01', output_path='src/data/cf_data.csv')
