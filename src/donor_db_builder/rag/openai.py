from typing import Optional, List
from pathlib import Path

from llama_index.core import SQLDatabase, Settings
from llama_index.llms.openai import OpenAI
from llama_index.core.query_engine import NLSQLTableQueryEngine

from .base import BaseRAG
from dotenv import load_dotenv
import os
from loguru import logger

load_dotenv()


class OpenAIRAG(BaseRAG):
    """RAG model using OpenAI's LLM backend"""

    api_key = os.getenv("OPENAI_API_KEY")

    def __init__(
        self,
        database: SQLDatabase,
        tables: List[str],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.0,
        vector_store_path: Optional[Path] = None,
    ):
        super().__init__(database, tables, vector_store_path)

        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
            )

        self.model = model
        self.temperature = temperature

    def initialize_llm(self) -> OpenAI:
        """Initialize OpenAI LLM"""
        try:
            llm = OpenAI(
                model=self.model,
                temperature=self.temperature,
                openai_api_key=self.api_key,
            )
            logger.info(f"Using OpenAI LLM: {self.model}")
            Settings.llm = llm
            return llm
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI LLM: {str(e)}")
            raise

    def setup_query_engine(self) -> None:
        """Set up NLSQLTableQueryEngine with OpenAI LLM"""
        try:
            llm = self.initialize_llm()
            self.query_engine = NLSQLTableQueryEngine(
                sql_database=self.sql, tables=self.tables, llm=llm
            )
            logger.info("Natural language query engine set up successfully")
        except Exception as e:
            logger.error(f"Failed to set up query engine: {str(e)}")
            raise
