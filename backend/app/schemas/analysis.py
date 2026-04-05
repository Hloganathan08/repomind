from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class AnalysisResponse(BaseModel):
    id: str
    repo_id: str
    status: str
    architecture_summary: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    entry_points: Optional[List[str]] = None
    onboarding_guide: Optional[str] = None
    files_analyzed: int
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class FileNodeResponse(BaseModel):
    id: str
    repo_id: str
    path: str
    name: str
    file_type: Optional[str] = None
    size_bytes: int
    ai_summary: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    message: str
    history: List[dict] = []


class ChatResponse(BaseModel):
    response: str
