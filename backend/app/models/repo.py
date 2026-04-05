from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.database import Base


class Repo(Base):
    __tablename__ = "repos"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    github_repo_id = Column(String, nullable=True)
    full_name = Column(String, nullable=False)  # e.g. "facebook/react"
    owner = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    language = Column(String, nullable=True)
    stars = Column(Integer, default=0)
    is_private = Column(Boolean, default=False)
    default_branch = Column(String, default="main")
    status = Column(String, default="pending")  # pending, analyzing, ready, error
    file_count = Column(Integer, default=0)
    analyzed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user_rel = relationship("User", back_populates="repos")
    file_nodes = relationship("FileNode", back_populates="repo", cascade="all, delete-orphan")
    analyses = relationship("Analysis", back_populates="repo", cascade="all, delete-orphan")
    chats = relationship("Chat", back_populates="repo", cascade="all, delete-orphan")