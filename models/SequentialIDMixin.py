from typing import Optional, Type, ClassVar
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, Integer, Sequence


# class SequentialIDMixin(SQLModel):
#     """Automatically creates a sequential ID column"""
#
#     # Class variable to store the column definition
#     _id_column: ClassVar[Column] = Column(
#         Integer,
#         Sequence("base_seq"),  # This will be replaced per-class
#         server_default=Sequence("base_seq").next_value(),
#         primary_key=True,
#     )
#
#     id: Optional[int] = Field(sa_column=_id_column, description="Primary key")
#
#     def __init_subclass__(cls, **kwargs):
#         """Initialize subclass with correct sequence name"""
#         super().__init_subclass__(**kwargs)
#         table_name = getattr(cls, "__tablename__", cls.__name__.lower())
#         seq = Sequence(f"{table_name}_seq")
#
#         # Create new column with correct sequence
#         cls._id_column = Column(
#             Integer,
#             seq,
#             server_default=seq.next_value(),
#             primary_key=True,
#         )
#
#         # Update the Field definition
#         if hasattr(cls, "id"):
#             cls.__fields__["id"].field_info.sa_column = cls._id_column

# class SequentialIDMixin(SQLModel):
#     """Automatically creates a sequential ID column"""
#
#     id: Optional[int] = Field(description="Primary key")
#
#     def __init_subclass__(cls, **kwargs):
#         """Initialize subclass with correct sequence name"""
#         super().__init_subclass__(**kwargs)
#
#         # Get table name from class
#         table_name = getattr(cls, "__tablename__", cls.__name__.lower())
#
#         # Create a new sequence for this specific table
#         seq = Sequence(f"{table_name}_seq")
#
#         # Create a new column instance for this specific table
#         id_column = Column(
#             Integer,
#             seq,
#             server_default=seq.next_value(),
#             primary_key=True,
#         )
#
#         # Update the Field definition with the new column
#         if hasattr(cls, "id"):
#             cls.__fields__["id"].field_info.sa_column = id_column


# class SequentialIDMixin(SQLModel):
#     """Automatically creates a sequential ID column"""
#
#     @classmethod
#     def _get_id_column(cls) -> Column:
#         """Create the ID column with sequence."""
#         # Get table name from class
#         table_name = getattr(cls, "__tablename__", cls.__name__.lower())
#
#         # Create sequence for this specific table
#         seq = Sequence(f"{table_name}_seq")
#
#         # Return new column instance
#         return Column(
#             Integer,
#             seq,
#             server_default=seq.next_value(),
#             primary_key=True,
#         )
#
#     # Define id with sa_column directly
#     id: Optional[int] = Field(
#         default=None, sa_column=_get_id_column(), description="Primary key"
#     )
#
#     class Config:
#         arbitrary_types_allowed = True
#
# class SequentialIDMixin(SQLModel):
#     """Automatically creates a sequential ID column"""
#
#     @staticmethod
#     def _get_id_column() -> Column:
#         """Create the ID column with sequence.
#         Note: This will use a temporary sequence that gets replaced in __init_subclass__
#         """
#         # Use a temporary sequence that will be replaced
#         seq = Sequence('base_seq')
#         return Column(
#             Integer,
#             seq,
#             server_default=seq.next_value(),
#             primary_key=True,
#         )
#
#     # Define id with initial column
#     id: Optional[int] = Field(
#         default=None,
#         sa_column=_get_id_column(),
#         description="Primary key"
#     )
#
#     def __init_subclass__(cls, **kwargs):
#         """Initialize subclass with correct sequence name"""
#         super().__init_subclass__(**kwargs)
#
#         # Get table name from class
#         table_name = getattr(cls, "__tablename__", cls.__name__.lower())
#
#         # Create sequence for this specific table
#         seq = Sequence(f"{table_name}_seq")
#
#         # Create new column with correct sequence
#         id_column = Column(
#             Integer,
#             seq,
#             server_default=seq.next_value(),
#             primary_key=True,
#         )
#
#         # Update the Field definition
#         if hasattr(cls, "id"):
#             cls.__fields__["id"].field_info.sa_column = id_column
#
#     class Config:
#         arbitrary_types_allowed = True


# def create_sequential_id_mixin(table_name: str) -> Type[SQLModel]:
#     """Factory function that creates a new mixin class with a unique sequence"""
#
#     class SequentialIDMixin(SQLModel):
#         """Automatically creates a sequential ID column"""
#
#         # Create sequence specific to this table
#         _sequence = Sequence(f"{table_name}_seq")
#
#         # Create column with the table-specific sequence
#         _id_column = Column(
#             Integer,
#             _sequence,
#             server_default=_sequence.next_value(),
#             primary_key=True,
#         )
#
#         # Define id field with the table-specific column
#         id: Optional[int] = Field(
#             default=None, sa_column=_id_column, description="Primary key"
#         )
#
#         class Config:
#             arbitrary_types_allowed = True
#
#     # Give the mixin a unique name for better debugging
#     SequentialIDMixin.__name__ = f"SequentialIDMixin_{table_name}"
#
#     return SequentialIDMixin
