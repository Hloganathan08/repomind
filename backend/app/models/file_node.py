from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.database import Base


class FileNode(Base):
    __tablename__ = "file_nodes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    repo_id = Column(String, ForeignKey("repos.id"), nullable=False, index=True)
    path = Column(String, nullable=False)         # e.g. "src/components/App.tsx"
    name = Column(String, nullable=False)         # e.g. "App.tsx"
    file_type = Column(String, nullable=True)     # e.g. "tsx", "py", "md"
    size_bytes = Column(Integer, default=0)
    ai_summary = Column(Text, nullable=True)      # AI-generated explanation
    imports = Column(JSON, nullable=True)         # list of files this file imports
    exports = Column(JSON, nullable=True)         # list of exports
    complexity_score = Column(Integer, default=0) # 1-10
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    repo = relationship("Repo", back_populates="file_nodes")