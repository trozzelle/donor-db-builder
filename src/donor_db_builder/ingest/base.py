from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Type, Any, Set
import pandas as pd
from sqlmodel import SQLModel
from donor_db_builder.database import SQLHandler
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

    # def insert(self, models: List[SQLModel]) -> None:
    #     try:
    #         with self.db.session() as session:
    #             session.add

    def _extract_nested_models(
        self, model: SQLModel, seen: Set[int] = None
    ) -> List[SQLModel]:
        """Recursively extract all nested models from relationships"""
        if seen is None:
            seen = set()

        # Skip the model if we've already seen it
        if id(model) in seen:
            return []

        seen.add(id(model))
        nested_models = []

        # Get all relationship attribute
        for attr_name, attr_value in vars(model).items():
            if isinstance(attr_value, SQLModel):
                nested_models.extend(self._extract_nested_models(attr_value, seen))
                nested_models.append(attr_value)
            elif isinstance(attr_value, list):
                for item in attr_value:
                    if isinstance(item, SQLModel):
                        nested_models.extend(self._extract_nested_models(item, seen))
                        nested_models.append(item)

        return nested_models
