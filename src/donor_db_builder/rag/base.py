from abc import ABC, abstractmethod
from typing import Optional, List, Any
from pathlib import Path

from llama_index.core import SQLDatabase, VectorStoreIndex
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.core.indices.struct_store import SQLTableRetrieverQueryEngine


class BaseRAG(ABC):
    """Abstract base class for RAG models."""

    def __init__(
        self,
        database: SQLDatabase,
        tables: List[str],
        vector_store_path: Optional[Path] = None,
    ):
        self.sql = database
        self.tables = tables
        self.vector_store_path = vector_store_path
        self.query_engine = None

    @abstractmethod
    def initialize_llm(self) -> Any:
        """Initialize the LLM backend"""

    @abstractmethod
    def setup_query_engine(self) -> None:
        """Set up the query engine for the initialized LLM"""

    def query(self, query_text: str) -> str:
        """Execute a natural language query against the provided tables"""
        if not self.query_engine:
            raise RuntimeError("Query engine not initialized")

        response = self.query_engine.query(query_text)
        return str(response)
