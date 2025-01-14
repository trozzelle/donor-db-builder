from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional
import dlt
from dlt.common import pendulum
from dlt.sources import TDataItems
from pydantic import BaseModel


class BasePipeline(ABC):
    """Abstract base class for DLT pipelines."""

    def __init__(
        self,
        pipeline_name: str,
        dataset_name: str,
        destination: str,
        schema_models: Optional[List[BaseModel]] = None,
    ):
        self.pipeline_name = pipeline_name
        self.dataset_name = dataset_name
        self.destination = destination
        self.schema_models = schema_models or []
        self.pipeline = self._create_pipeline()

    def _create_pipeline(self) -> dlt.Pipeline:
        """Create a DLT pipeline"""
        return dlt.pipeline(
            pipeline_name=self.pipeline_name,
            destination=self.destination,
            dataset_name=self.dataset_name,
            schema_models=self.schema_models,
        )

    @abstractmethod
    def extract(self) -> TDataItems:
        """Extract data from source"""
        pass

    @abstractmethod
    def transform(self, data: TDataItems) -> TDataItems:
        """Transform data"""
        pass

    @abstractmethod
    def load(self, data: TDataItems) -> None:
        """Load data into destination"""
