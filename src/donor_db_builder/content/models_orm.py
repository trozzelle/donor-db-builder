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

    id: int | None = Field(
        default_factory=id_field("webcontent"),
        description="The row id of the record in the database",
    )
    uid: str = Field(description="UUID for the record in the database")
    url: HttpUrl = Field(sa_type=AutoString, description="The URL to the web page")
    domain: str = Field(index=True, description="The domain of the web page")
    title: Optional[str] = Field(None, description="The title of the web page")
    content: str = Field(description="A JSON string of the extracted trafilatura data")
    site_meta: str = Field(description="The site meta data of the web page")
    fetched_at: datetime = Field(description="The date the web page was fetched")
    donor_id: Optional[str] = Field(
        default=None,
        index=True,
        description="The donor id of the entity the web page may relate to",
    )
    tags: str = Field(description="The tags associated with the web page")


class ContentMetadata(SQLModel, table=True):
    """Model for content metadata"""

    id: int | None = id_field("contentmetadata")
    author: Optional[str]
    date: Optional[datetime]
    categories: str
    language: Optional[str]
