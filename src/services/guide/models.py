"""Pydantic models for guide service."""

from typing import List, Optional
from pydantic import BaseModel


class DocumentMetadata(BaseModel):
    """Metadata for a document."""
    title: str
    path: str
    breadcrumbs: List[str]
    content_type: str = "text/html"


class TemplateData(BaseModel):
    """Data for HTML template rendering."""
    title: str
    content: str
    breadcrumbs: List[str]
    base_url: str = "/guide"