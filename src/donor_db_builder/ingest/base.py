from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Type, Any
import pandas as pd
from sqlmodel import SQLModel
from ..database import SQLHandler
from loguru import logger

class DataIngestor(ABC):
    """Base class for data ingestion handler"""

    def __init__(self, db: SQLHandler):
        self.db = db

    @abstractmethod
    def transform_record(self, record: Dict[str, Any]) -> SQLModel:
        """Transform record into appropriate SQLModel"""
        pass

    def read_csv(self, file_path: Path) -> pd.DataFrame:
        """Loads CSV into DataFrame"""
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            logger.error(f"Failed to load CSV: {e}")
            raise

    def insert(self, models: List[SQLModel]) -> None:
        try:
            with self.db.session() as session:
                session.add