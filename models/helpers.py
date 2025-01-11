from sqlalchemy import Column, Integer, String, Sequence
from sqlmodel import Field


def generate_id_sequence(table_name: str):
    """Generates auto-incrementing id field, necessary
    since DuckDB doesn't yet support Postgres SERIAL type"""

    def create_id_field() -> Field:
        sequence = Sequence(f"{table_name}_seq")
        return Field(
            default=None,
            primary_key=True,
            sa_column_args=[sequence],
            sa_column_kwargs={
                "primary_key": True,
                "server_default": sequence.next_value(),
            },
        )

    return create_id_field
