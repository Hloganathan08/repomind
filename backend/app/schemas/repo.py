from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RepoCreate(BaseModel):
    full_name: str  # e.g. "facebook/react"


class RepoResponse(BaseModel):
    id: str
    full_name: str
    owner: str
    name: str
    description: Optional[str] = None
    language: Optional[str] = None
    stars: int
    status: str
    file_count: int
    analyzed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True