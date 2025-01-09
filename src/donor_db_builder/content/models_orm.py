from typing import Optional
from datetime import datetime
from dataclasses import field
from pydantic import BaseModel, HttpUrl
from sqlalchemy import Column, Integer, String, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlmodel import Field, SQLModel, AutoString

Base = declarative_base()


def id_field(table_name: str):
    """Generates auto-incrementing id field, necessary
    since DuckDB doesn't yet support Postgres SERIAL type"""

    sequence = Sequence(f"{table_name}_seq")
    return Field(
        default=None,
        primary_key=True,
        sa_column_args=[sequence],
        sa_column_kwargs={"server_default": sequence.next_value()},
    )


class WebContent(SQLModel, table=True):
    """Model for web page content"""

    id: int | None = id_field("webcontent")
    uid: str
    url: HttpUrl = Field(sa_type=AutoString)
    domain: str = Field(index=True)
    title: Optional[str]
    content: str
    site_meta: str
    fetched_at: datetime
    donor_id: Optional[str] = Field(default=None, index=True)
    tags: str


class ContentMetadata(SQLModel, table=True):
    """Model for content metadata"""

    id: int | None = id_field("contentmetadata")
    author: Optional[str]
    date: Optional[datetime]
    categories: str
    language: Optional[str]
