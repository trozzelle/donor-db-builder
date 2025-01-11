from abc import ABC, abstractmethod
from typing import Optional, Any, Dict, List
from pathlib import Path
from contextlib import contextmanager


class DatabaseHandler(ABC):
    """Abstract base class for database handlers."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path
        self.engine = None

    @abstractmethod
    def create_engine(self) -> None:
        """Create the database engine and connect to the database."""
        pass

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the database and write schema if necessary."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the database connection."""
        pass

    @contextmanager
    def session(self):
        """Context manager for database sessions"""
        try:
            session = self._create_session()
            yield session
        finally:
            session.close()

    @abstractmethod
    def _create_session(self):
        """Create a new database session."""
        pass
