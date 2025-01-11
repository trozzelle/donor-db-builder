"""Module containing custom exceptions used in the database handling classes"""


class DatabaseError(Exception):
    """Base exception for database errors"""

    pass


class DatabaseConnectionError(DatabaseError):
    """Raised when database connection fails"""

    pass


class DatabaseInitializationError(DatabaseError):
    """Raised when database initialization fails"""

    pass


class SessionCreationError(DatabaseError):
    """Raised when session creation fails"""

    pass


class DatabaseOperationError(DatabaseError):
    """Raised when database operation fails"""

    pass
