from typing import Optional, Type
from pathlib import Path

from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy import Engine
from .base import DatabaseHandler
from loguru import logger
from .exceptions import (
    DatabaseConnectionError,
    DatabaseInitializationError,
    SessionCreationError,
    DatabaseOperationError,
)


class SQLHandler(DatabaseHandler):
    """Handler for SQL databases (specifically DuckDB)."""

    def __init__(
        self,
        db_path: Optional[Path] = None,
        models: Optional[Type[SQLModel]] = None,
        echo: bool = False,
    ):
        try:
            super().__init__(db_path)
            self.models = models or []
            self.echo = echo
            self.db_url = f"duckdb:///{db_path}" if db_path else None

            if not db_path:
                raise ValueError("Database path is required")

            self.create_engine()
            self.initialize()
        except Exception as e:
            logger.error(f"Failed to initialize SQL handler {str(e)}")
            raise DatabaseInitializationError("Database initialization failed") from e

    def create_engine(self) -> Engine:
        """Connect to the database and return an engine object."""
        try:
            self.engine = create_engine(self.db_url, echo=self.echo)
            return self.engine
        except SQLAlchemyError as e:
            logger.error(f"Failed to create database engine {str(e)}")
            raise DatabaseConnectionError("Could not create database engine") from e

    def initialize(self) -> None:
        """Initialize the database and write schema if necessary."""
        try:
            self.engine = create_engine(self.db_url, echo=self.echo)
            SQLModel.metadata.create_all(self.engine)
            logger.info("Successfully created database schema")
        except SQLAlchemyError as e:
            logger.error(f"Failed to create database schema: {str(e)}")
            raise DatabaseInitializationError("Could not create database schema") from e

    def close(self) -> None:
        """Close the database connection."""
        if self.engine:
            try:
                if self.engine:
                    self.engine.dispose()
                    logger.info("Database connection closed successfully")
            except Exception as e:
                logger.error(f"Error closing database connection: {str(e)}")
                raise DatabaseOperationError(
                    "Could not close database connection"
                ) from e

    def _create_session(self):
        """Create a new database session."""
        try:
            return Session(self.engine)
        except SQLAlchemyError as e:
            logger.error(f"Failed to create database session: {str(e)}")
            raise SessionCreationError("Could not create database session") from e
