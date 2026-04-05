from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.models.repo import Repo
from app.schemas.repo import RepoCreate, RepoResponse
from app.api.dependencies import get_current_user
from app.services.github_service import fetch_repo_info
from app.workers.tasks import analyze_repo_task

import asyncio

router = APIRouter(prefix="/repos", tags=["repos"])


@router.post("", response_model=RepoResponse, status_code=201)
def add_repo(
    payload: RepoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = db.query(Repo).filter(
        Repo.user_id == current_user.id,
        Repo.full_name == payload.full_name,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Repo already added")

    github_data = asyncio.run(fetch_repo_info(payload.full_name))
    if not github_data:
        raise HTTPException(status_code=404, detail="GitHub repo not found")

    repo = Repo(user_id=current_user.id, **github_data, status="pending")
    db.add(repo)
    db.commit()
    db.refresh(repo)
    return repo


@router.post("/{repo_id}/analyze", status_code=202)
def trigger_analysis(
    repo_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = db.query(Repo).filter(
        Repo.id == repo_id,
        Repo.user_id == current_user.id,
    ).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repo not found")
    if repo.status == "analyzing":
        raise HTTPException(status_code=400, detail="Analysis already in progress")

    analyze_repo_task.delay(repo_id)
    return {"message": "Analysis started", "repo_id": repo_id}


@router.get("", response_model=list[RepoResponse])
def list_repos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Repo).filter(Repo.user_id == current_user.id).all()


@router.get("/{repo_id}", response_model=RepoResponse)
def get_repo(
    repo_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = db.query(Repo).filter(
        Repo.id == repo_id,
        Repo.user_id == current_user.id,
    ).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repo not found")
    return repo