from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    repo_id = Column(String, ForeignKey("repos.id"), nullable=False, index=True)
    status = Column(String, default="pending")    # pending, running, complete, error
    architecture_summary = Column(Text, nullable=True)
    tech_stack = Column(JSON, nullable=True)      # list of detected technologies
    entry_points = Column(JSON, nullable=True)    # key files to understand first
    dependency_graph = Column(JSON, nullable=True) # node/edge data for D3 graph
    onboarding_guide = Column(Text, nullable=True) # AI-generated onboarding doc
    files_analyzed = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    repo = relationship("Repo", back_populates="analyses")