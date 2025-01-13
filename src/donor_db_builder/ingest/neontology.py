from typing import Dict, Any, List
from pathlib import Path

import pandas as pd
from neontology import init_neontology
from models.GraphModels import (
    Individual,
    Organization,
    Location,
    Filer,
    Payment,
    DonatedIndRel,
    DonatedOrgRel,
    ReceivedRel,
    LocatedIndRel,
    LocatedOrgRel,
    LocatedFilerRel,
)
from donor_db_builder.ingest.base import DataIngestor
from loguru import logger
from pathlib import Path


class NeontologyIngestor(DataIngestor):
    """Handler for the neontology ORM"""

    def __init__(self, db_handler, data_dir: Path):
        # super().__init__(db_handler)
        try:
            init_neontology(db_handler)
        except Exception as e:
            logger.error(f"Failed to initialize neontology: {str(e)}")
            raise

        self.data_dir = data_dir
        self.filer_data = None
        self.transaction_data = None

    def load_data(self) -> None:
        """Load all dependent CSV files"""
        try:
            self.filer_data = pd.read_csv(
                self.data_dir / "cf_filers.csv", keep_default_na=False
            )
            self.transaction_data = pd.read_csv(
                self.data_dir / "cf_data.csv", keep_default_na=False
            )
            logger.info("Successfully loaded CSV files")
        except Exception as e:
            logger.error(f"Failed to load CSV files: {str(e)}")
            raise

    def transform_record(self):
        pass

    def transform_filer(self, record: Dict[str, Any]) -> Filer:
        """Transform filer record into Filer model"""
        location = {
            "street_address": record.get("ADDRESS"),
            "city": record.get("CITY"),
            "state": record.get("STATE"),
            "zip_code": record.get("ZIPCODE"),
        }

        filer = {
            "filer_id": record.get("FILER_ID"),
            "filer_name": record.get("FILER_NAME"),
            "compliance_type": record.get("COMPLIANCE_TYPE_DESC"),
            "committee_type": record.get("COMMITTEE_TYPE_DESC"),
            "filer_type": record.get("FILER_TYPE_DESC"),
            "filer_status": record.get("FILER_STATUS"),
            "office": record.get("OFFICE_DESC"),
            "district": record.get("DISTRICT"),
            "county": record.get("COUNTY_DESC"),
            "location": location,
        }

        return filer, location

    def transform_payment(
        self, record: Dict[str, Any], filer_map: Dict[int, int]
    ) -> Payment:
        """Transform payment record into Payment model"""
        # Create either Individual or Organization based on type
        # If the record has an entity name, treat it as an organization
        # this isn't perfect but suffices for development until
        # definable logic is implemented

        location = Location(
            street_address=record.get("FLNG_ENT_ADD1"),
            city=record.get("FLNG_ENT_CITY"),
            state=record.get("FLNG_ENT_STATE"),
            zip_code=record.get("FLNG_ENT_ZIP"),
            country=record.get("FLNG_ENT_COUNTRY"),
        )

        if record["FLNG_ENT_NAME"] is None or len(record["FLNG_ENT_NAME"]) == 0:
            payer = Individual(
                first_name=record.get("FLNG_ENT_FIRST_NAME"),
                last_name=record.get("FLNG_ENT_LAST_NAME"),
                location=location,
            )
        else:
            payer = Organization(
                name=record.get("FLNG_ENT_NAME"),
                location=location,
            )

        filer = filer_map.get(record.get("FILER_ID"))
        if not filer:
            logger.warning(f"Filer {record.get('FILER_ID')} not found")

        payment = Payment(
            amount=record["ORG_AMT"],
            date=record["SCHED_DATE"],
            transaction_id=record["TRANS_NUMBER"],
            type=record["FILING_SCHED_DESC"],
            payer_type=record["CNTRBR_TYPE_DESC"],
            payer_id=payer.id,
            filer=filer,
            payer=payer,
        )

        return payment, payer

    # def bulk_insert(self, models: List[SQLModel], batch_size: int = 1000) -> None:
    #     """Insert records into the database in batches in a single session"""
    #
    #     try:
    #         for i in range(0, len(models), batch_size):
    #             batch = models[i : i + batch_size]
    #
    #     except Exception as e:
    #         logger.error(f"Failed to insert records: {e}")
    #         raise

    def ingest(self) -> None:
        """Perform ingestion of campaign finance data"""
        try:
            logger.info("Starting campaign finance data ingestion")
            self.load_data()

            # Transform and insert filers first
            logger.info("Processing filer records")
            filers_and_locations = [
                self.transform_filer(record)
                for record in self.filer_data.to_dict("records")
            ]

            filers, locations = zip(*filers_and_locations)

            filers_df = pd.DataFrame.from_records(filers)
            locations_df = pd.DataFrame.from_records(locations)

            Filer.merge_df(filers_df)
            Location.merge_df(locations_df)
            # self.bulk_insert(models=filers, batch_size=self.batch_size)
            # logger.info(f"Completed filer ingestion: {len(filers)} records")
            #
            # # filer_map = {filer.id for filer in filers}
            # # filer_map = {filer.filer_id: filer.id for filer in filers}
            # filer_map = {filer.filer_id: filer for filer in filers}
            # # Transform and insert payments (with nested individuals/organizations)
            # logger.info("Processing payment records")
            # payments_and_payers = [
            #     self.transform_payment(record, filer_map)
            #     for record in self.transaction_data.to_dict("records")
            # ]
            #
            # # Payer and payment insert split because payer objects (Individual, Organization)
            # # don't have an id until they're inserted into the database and generated from sequence
            # payments, payers = zip(*payments_and_payers)
            #
            # logger.info("Inserting payers")
            # self.bulk_insert(models=payers, batch_size=self.batch_size)
            #
            # for payment, payer in zip(payments, payers):
            #     payment.payer_id = payer.id
            #
            # logger.info("Inserting payments")
            # self.bulk_insert(
            #     models=payments, session=session, batch_size=self.batch_size
            # )
            #
            # # self.bulk_insert(payments, batch_size=self.batch_size)
            # # logger.info(f"Completed payment ingestion: {len(payments)} records")
            #
            # session.commit()
            # logger.info("Campaign finance data ingestion completed successfully")

        except Exception as e:
            logger.error(f"Campaign finance ingestion failed: {str(e)}")
            raise
