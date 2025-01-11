from typing import Dict, Any, List
from pathlib import Path
import pandas as pd
from models.SQLModels import Individual, Organization, Location, Payment, Filer
from .base import DataIngestor
from loguru import logger


class CampaignFinanceIngestor(DataIngestor):
    """Handles ingestion of campaign finance data."""

    def __init__(self, db_handler, data_dir: Path):
        super().__init__(db_handler)
        self.data_dir = data_dir
        self.filer_data = None
        self.transaction_data = None
        self.batch_size = 1000

    def load_data(self) -> None:
        """Load all dependent CSV files"""
        try:
            self.filer_data = pd.read_csv(self.data_dir / "cf_filers.csv")
            self.transaction_data = pd.read_csv(self.data_dir / "cf_data.csv")
            logger.info("Successfully loaded CSV files")
        except Exception as e:
            logger.error(f"Failed to load CSV files: {str(e)}")
            raise

    def transform_filer(self, record: Dict[str, Any]) -> Filer:
        """Transform filer record into Filer model"""
        location = Location(
            street=record.get("ADDRESS"),
            city=record.get("CITY"),
            state=record.get("STATE"),
            zip_code=record.get("ZIPCODE"),
        )

        return Filer(
            filer_id=record.get("FILER_ID"),
            filer_name=record.get("FILER_NAME"),
            compliance_type=record.get("COMPLIANCE_TYPE_DESC"),
            committee_type=record.get("COMMITTEE_TYPE_DESC"),
            filer_type=record.get("FILER_TYPE_DESC"),
            filer_status=record.get("FILER_STATUS"),
            office=record.get("OFFICE_DESC"),
            district=record.get("DISTRICT"),
            county=record.get("COUNTY_DESC"),
            location=location,
        )

    def transform_payment(self, record: Dict[str, Any]) -> Payment:
        """Transform payment record into Payment model"""
        # Create either Individual or Organization based on type
        if record["payer_type"] == "individual":
            payer = Individual(
                first_name=record.get("FLNG_ENT_FIRST_NAME"),
                last_name=record.get("FLNG_ENT_LAST_NAME"),
                location=Location(
                    street=record.get("FLNG_ENT_ADD1"),
                    city=record.get("FLNG_ENT_CITY"),
                    state=record.get("FLNG_ENT_STATE"),
                    zip_code=record.get("FLNG_ENT_ZIP"),
                    country=record.get("FLNG_ENT_COUNTRY"),
                ),
            )
        else:
            payer = Organization(
                name=record.get("FLNG_ENT_NAME"),
                location=Location(
                    street=record.get("FLNG_ENT_ADD1"),
                    city=record.get("FLNG_ENT_CITY"),
                    state=record.get("FLNG_ENT_STATE"),
                    zip_code=record.get("FLNG_ENT_ZIP"),
                    country=record.get("FLNG_ENT_COUNTRY"),
                ),
            )

        return Payment(
            amount=record["ORG_AMOUNT"],
            date=record["SCHED_DATE"],
            payer_type=record["CNTRBR_TYPE_DESC"],
            payer=payer,
        )

    def ingest(self) -> None:
        """Perform ingestion of campaign finance data"""
        try:
            logger.info("Starting campaign finance data ingestion")
            self.load_data()

            # Transform and insert filers first
            logger.info("Processing filer records")
            filers = [
                self.transform_filer(record)
                for record in self.filer_data.to_dict("records")
            ]
            self.bulk_insert(filers, batch_size=self.batch_size)
            logger.info(f"Completed filer ingestion: {len(filers)} records")

            # Transform and insert payments (with nested individuals/organizations)
            logger.info("Processing payment records")
            payments = [
                self.transform_payment(record)
                for record in self.transaction_data.to_dict("records")
            ]
            self.bulk_insert(payments, batch_size=self.batch_size)
            logger.info(f"Completed payment ingestion: {len(payments)} records")

            logger.info("Campaign finance data ingestion completed successfully")

        except Exception as e:
            logger.error(f"Campaign finance ingestion failed: {str(e)}")
            raise
