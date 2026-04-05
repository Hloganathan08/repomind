from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.models.repo import Repo
from app.models.analysis import Analysis
from app.models.file_node import FileNode
from app.schemas.analysis import AnalysisResponse, FileNodeResponse, ChatRequest, ChatResponse
from app.api.dependencies import get_current_user
import anthropic
from app.core.config import settings

router = APIRouter(tags=["analysis"])


@router.get("/repos/{repo_id}/analyses", response_model=list[AnalysisResponse])
def get_analyses(
    repo_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = db.query(Repo).filter(Repo.id == repo_id, Repo.user_id == current_user.id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repo not found")
    return db.query(Analysis).filter(Analysis.repo_id == repo_id).order_by(Analysis.created_at.desc()).all()


@router.get("/repos/{repo_id}/files", response_model=list[FileNodeResponse])
def get_files(
    repo_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = db.query(Repo).filter(Repo.id == repo_id, Repo.user_id == current_user.id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repo not found")
    return db.query(FileNode).filter(FileNode.repo_id == repo_id).all()


@router.post("/repos/{repo_id}/chat", response_model=ChatResponse)
def chat_with_repo(
    repo_id: str,
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = db.query(Repo).filter(Repo.id == repo_id, Repo.user_id == current_user.id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repo not found")

    analysis = db.query(Analysis).filter(
        Analysis.repo_id == repo_id,
        Analysis.status == "complete"
    ).order_by(Analysis.created_at.desc()).first()

    files = db.query(FileNode).filter(FileNode.repo_id == repo_id).limit(30).all()
    file_context = "\n".join([f"- {f.path}: {f.ai_summary or ''}" for f in files])

    system_prompt = f"""You are an expert code assistant for the repository {repo.full_name}.

Architecture: {analysis.architecture_summary if analysis else 'Not yet analyzed'}
Tech stack: {', '.join(analysis.tech_stack or []) if analysis else 'Unknown'}

Files in this codebase:
{file_context}

Answer questions about this codebase concisely and accurately."""

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    messages = []
    for msg in payload.history[-10:]:
        if msg.get("role") in ("user", "assistant"):
            messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": payload.message})

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1000,
        system=system_prompt,
        messages=messages,
    )

    return {"response": response.content[0].text}
