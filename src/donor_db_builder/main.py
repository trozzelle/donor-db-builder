from pathlib import Path

import pandas as pd
import utils.cleaning as clean
from dotenv import dotenv_values
from utils.helpers import _generate_uuid

from models.Filer import Filer
from models.Donor import Donor, _donor_name, _set_type
from models.Contribution import Contribution
from src.donor_db_builder.parallel_processor import ParallelProcessor
from src.donor_db_builder.processors import process_nodes, process_relationships
from src.donor_db_builder.utils.logger import Logger

config = dotenv_values(".env")

"""
Adhoc script for development
"""
if __name__ == "__main__":
    Logger.setup_logger(app_name="donor_db_builder")
    logger = Logger.get_logger()
    logger.info("Starting Donor DB Builder")

    contributions_df = pd.read_csv(Path.cwd() / "data" / "cf_data.csv", escapechar="\\")
    filers_df = pd.read_csv(Path.cwd() / "data" / "cf_filers.csv", escapechar="\\")

    uri = f"bolt://localhost:7687"
    username = "tr"
    password = "memgraph"

    # contributions_df['ID'] = contributions_df.apply(lambda _: str(uuid.uuid4()), axis=1)

    # db = DonorGraph(host="localhost", port=7687, username="", password="")
    # db.clear_database()

    logger.info("Preparing donor data")
    contributions_df["donor_type"] = contributions_df["FLNG_ENT_FIRST_NAME"].apply(
        _set_type
    )

    contributions_df["donor_name"] = contributions_df.apply(_donor_name, axis=1)

    contributions_df["donor_id"] = contributions_df.apply(
        clean.generate_donor_id, axis=1
    )

    # Initialize the parallel processor
    processor = ParallelProcessor(num_processes=16)

    # Database configuration
    db_config = {
        "host": "localhost",
        "port": 7687,
        "username": "tr",
        "password": "memgraph",
    }

    filer_transformers = {"id": _generate_uuid}

    filer_mappings = {
        "id": "id",  # Will be generated
        "filer_id": "FILER_ID",
        "name": "FILER_NAME",
        "type": "FILER_TYPE_DESC",
        "compliance_type": "COMPLIANCE_TYPE_DESC",
        "committee_type": "COMMITTEE_TYPE_DESC",
        "status": "FILER_STATUS",
        "office": "OFFICE_DESC",
        "district": "DISTRICT",
        "county": "COUNTY_DESC",
        "municipality": "MUNICIPALITY",
        "subdivision": "SUBDIVISION",
    }

    # Process nodes in parallel
    processor.process_in_parallel(
        df=filers_df,
        processor_func=process_nodes,
        db_config=db_config,
        additional_args={
            "model": Filer,
            "field_mappings": filer_mappings,
            "identifier_field": "id",
            "transformers": filer_transformers,
        },
        chunk_size=4000,
    )

    donor_mappings = {
        "id": "donor_id",
        "name": "donor_name",
        "type": "donor_type",
        "address": "FLNG_ENT_ADD1",
        "city": "FLNG_ENT_CITY",
        "state": "FLNG_ENT_STATE",
        "zip": "FLNG_ENT_ZIP",
    }

    # Process nodes in parallel
    processor.process_in_parallel(
        df=contributions_df,
        processor_func=process_nodes,
        db_config=db_config,
        additional_args={
            "model": Donor,
            "field_mappings": donor_mappings,
            "identifier_field": "id",
        },
        chunk_size=1000,
    )

    contribution_mappings = {
        "transaction_id": "TRANS_NUMBER",
        "amount": "ORG_AMT",
        "date": "SCHED_DATE",
        "payment_type": "PAYMENT_TYPE_DESC",
        "contributor_type": "CNTRBR_TYPE_DESC",
        "payment_method": "PAYMENT_TYPE_DESC",
    }

    contribution_transformers = {
        # 'amount': float,
        # 'date': lambda x: f"datetime('{x}')"
    }

    # Process relationships in parallel
    processor.process_in_parallel(
        df=contributions_df,
        processor_func=process_relationships,
        db_config=db_config,
        additional_args={
            "model": Contribution,
            "field_mappings": contribution_mappings,
            "start_node_match": {"Donor": {"id": "donor_id"}},
            "end_node_match": {"Filer": {"filer_id": "FILER_ID"}},
            "start_relationship_type": "MADE",
            "end_relationship_type": "TO",
            "transformers": contribution_transformers,
        },
        chunk_size=1000,
    )
