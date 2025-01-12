from typing import Optional
from datetime import datetime
from dataclasses import field
from pydantic import BaseModel, HttpUrl


class WebContent(BaseModel):
    """Model for web page content"""

    id: str
    url: HttpUrl
    domain: str
    title: Optional[str]
    content: str
    metadata: dict
    fetched_at: datetime
    donor_id: Optional[str] = None
    tags: list[str] = field(default_factory=list)


class ContentMetadata(BaseModel):
    """Model for content metadata"""

    author: Optional[str]
    date: Optional[datetime]
    categories: list[str] = field(default_factory=list)
    language: Optional[str]
