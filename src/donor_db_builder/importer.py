from neo4j import GraphDatabase
import pandas as pd
import hashlib
import re
from loguru import logger
import numpy as np
from src.donor_db_builder.utils.logger import Logger

logger = Logger.get_logger()

class DonorGraph:
    def __init__(self, uri: str, username: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))

        logger.info("Initializing CampaignFinanceGraph with URI: {}", uri)

    def close(self):
        logger.info("Closing Neo4j connection")
        self.driver.close()

    @logger.catch
    def clear_database(self):
        with self.driver.session() as session:
            logger.debug("Deleting all nodes and relationships")
            session.run("MATCH (n) DETACH DELETE n")
            logger.info("Database cleared successfully")

    def generate_donor_id(self, row: pd.Series) -> str:
        """Generate unique ID for donor by hashing their attributes"""
        if pd.isna(row['FLNG_ENT_FIRST_NAME']):
            key_parts = [
                str(row['FLNG_ENT_NAME']).upper(),
                str(row['FLNG_ENT_ADD1']).upper(),
                str(row['FLNG_ENT_ZIP'])[:5]
            ]
        else:
            key_parts = [
                str(row['FLNG_ENT_FIRST_NAME']).upper(),
                str(row['FLNG_ENT_LAST_NAME']).upper(),
                str(row['FLNG_ENT_ADD1']).upper(),
                str(row['FLNG_ENT_ZIP'])[:5]
            ]

        key = '|'.join(filter(None, key_parts))
        return hashlib.md5(key.encode()).hexdigest()

    def clean_name(self, name: str) -> str:

        if pd.isna(name):
            return ""

        name = re.sub(r'\s+(Inc\.?|LLC|Corp\.?|LLP)$', '', name, flags=re.IGNORECASE)

        return name.strip()

    @logger.catch
    def import_data(self, contributions_df: pd.DataFrame, filers_df: pd.DataFrame):

        logger.info("Starting data import")
        logger.info("Processing {} filers and {} contributions",
                    len(filers_df), len(contributions_df))

        try:
            with self.driver.session() as session:
                logger.info("Importing committees")

                ## Data cleanup
                # Split 'MUNICIPALITY_DESC, SUBDIVISION_DESC' column. This is concatenated into a single column in all
                # Socrata exports, not sure why
                filers_df[['MUNICIPALITY', 'SUBDIVISION']] = filers_df['MUNICIPALITY_DESC, SUBDIVISION_DESC'].str.split(',', expand=True)

                # Change NaN to None, interpreted as null by neo4j
                filers_df = filers_df.replace({np.nan: None})

                for i, row in filers_df.iterrows():
                    try:
                        session.run("""
                            MERGE (c:Committee {filer_id: $filer_id})
                            SET c.name = $name,
                                c.type = $type,
                                c.status = $status,
                                c.office = $office,
                                c.district = $district,
                                c.county = $county,
                                c.municipality = $municipality,
                                c.subdivision = $subdivision
                        """, {
                            'filer_id': str(row['FILER_ID']),
                            'name': row['FILER_NAME'],
                            'type': row['FILER_TYPE_DESC'],
                            'status': row['FILER_STATUS'],
                            'office': row['OFFICE_DESC'],
                            'district': row['DISTRICT'],
                            'county': row['COUNTY_DESC'],
                            'municipality': row['MUNICIPALITY'],
                            'subdivision': row['SUBDIVISION']
                        })
                        if (i + 1) % 100 == 0:
                            logger.debug(f"Processed {i+1} filers")
                    except Exception as e:
                        logger.error("Error importing committee %s: %s",
                                        row['FILER_ID'], str(e))
                        raise

                logger.info("Importing donors and contributions")

                ## Data cleanup

                # Parse date strings into python datetime objects
                contributions_df['SCHED_DATE'] = pd.to_datetime(contributions_df['SCHED_DATE'])
                # Change NaN to None, interpreted as null by neo4j
                contributions_df = contributions_df.replace({np.nan: None})

                for i, row in contributions_df.iterrows():
                    try:
                        donor_id = self.generate_donor_id(row)

                        if pd.isna(row['FLNG_ENT_FIRST_NAME']):
                            donor_type = 'Organization'
                            donor_name = self.clean_name(row['FLNG_ENT_NAME'])
                        else:
                            donor_type = 'Individual'
                            donor_name = f"{row['FLNG_ENT_FIRST_NAME']} {row['FLNG_ENT_LAST_NAME']}".strip()

                        session.run("""
                            MERGE (d:Donor {id: $donor_id})
                            SET d.name = $name,
                                d.type = $donor_type,
                                d.address = $address,
                                d.city = $city,
                                d.state = $state,
                                d.zip = $zip
                        """, {
                            'donor_id': donor_id,
                            'name': donor_name,
                            'donor_type': donor_type,
                            'address': row['FLNG_ENT_ADD1'],
                            'city': row['FLNG_ENT_CITY'],
                            'state': row['FLNG_ENT_STATE'],
                            'zip': row['FLNG_ENT_ZIP']
                        })

                        # Create Contribution and relationships
                        session.run("""
                            MATCH (d:Donor {id: $donor_id})
                            MATCH (c:Committee {filer_id: $filer_id})
                            CREATE (d)-[:MADE]->(t:Contribution {
                                amount: $amount,
                                date: date($date),
                                payment_type: $payment_type,
                                transaction_id: $transaction_id,
                                contributor_type: $contributor_type,
                                payment_method: $payment_method
                            })-[:TO]->(c)
                        """, {
                            'donor_id': donor_id,
                            'filer_id': str(row['FILER_ID']),
                            'amount': float(row['ORG_AMT']),
                            'date': row['SCHED_DATE'],
                            'payment_type': row['PAYMENT_TYPE_DESC'],
                            'transaction_id': row['TRANS_NUMBER'],
                            'contributor_type': row['CNTRBR_TYPE_DESC'],
                            'payment_method': row['PAYMENT_TYPE_DESC']
                        })
                        if (i + 1) % 100 == 0:
                            logger.debug(f"Processed {i + 1} contributions")
                    except Exception as e:
                        logger.error("Error importing contribution %s: %s",
                                        row['TRANS_NUMBER'], str(e))
                        raise

                logger.success("Data import completed successfully")

        except Exception as e:
            logger.error("Fatal error during data import: %s", str(e))
            raise

