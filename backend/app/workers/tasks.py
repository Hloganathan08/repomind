from app.workers.celery_app import celery_app
from app.db.database import SessionLocal
from app.models.repo import Repo
from app.models.file_node import FileNode
from app.models.analysis import Analysis
from app.services.github_service import fetch_repo_tree, fetch_file_content
from app.services.ai_service import summarize_file, analyze_architecture
from datetime import datetime, timezone
import asyncio


@celery_app.task(bind=True, max_retries=3)
def analyze_repo_task(self, repo_id: str):
    db = SessionLocal()
    try:
        repo = db.query(Repo).filter(Repo.id == repo_id).first()
        if not repo:
            return

        # Mark as running
        repo.status = "analyzing"
        analysis = Analysis(repo_id=repo_id, status="running", started_at=datetime.now(timezone.utc))
        db.add(analysis)
        db.commit()

        # Fetch file tree from GitHub
        tree = asyncio.run(fetch_repo_tree(repo.full_name, repo.default_branch))
        if not tree:
            raise Exception("Could not fetch repo tree")

        # Filter to code files only (skip binaries, lock files)
        code_extensions = {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs",
                           ".java", ".cpp", ".c", ".h", ".rb", ".php", ".swift",
                           ".kt", ".cs", ".md", ".yaml", ".yml", ".json", ".toml"}
        code_files = [
            f for f in tree
            if any(f["path"].endswith(ext) for ext in code_extensions)
            and f.get("size", 0) < 100000  # skip files > 100kb
        ][:50]  # analyze max 50 files

        # Create FileNode records and summarize each file
        file_nodes = []
        for file in code_files:
            content = asyncio.run(fetch_file_content(repo.full_name, file["path"], repo.default_branch))
            if not content:
                continue

            summary = asyncio.run(summarize_file(file["path"], content))

            node = FileNode(
                repo_id=repo_id,
                path=file["path"],
                name=file["path"].split("/")[-1],
                file_type=file["path"].rsplit(".", 1)[-1] if "." in file["path"] else "",
                size_bytes=file.get("size", 0),
                ai_summary=summary,
            )
            db.add(node)
            file_nodes.append({"path": file["path"], "summary": summary})

        db.commit()

        # Generate architecture summary
        arch_result = asyncio.run(analyze_architecture(repo.full_name, file_nodes))

        # Update analysis record
        analysis.status = "complete"
        analysis.architecture_summary = arch_result.get("architecture_summary")
        analysis.tech_stack = arch_result.get("tech_stack", [])
        analysis.entry_points = arch_result.get("entry_points", [])
        analysis.onboarding_guide = arch_result.get("onboarding_guide")
        analysis.files_analyzed = len(file_nodes)
        analysis.completed_at = datetime.now(timezone.utc)

        # Update repo
        repo.status = "ready"
        repo.file_count = len(file_nodes)
        repo.analyzed_at = datetime.now(timezone.utc)
        db.commit()

    except Exception as e:
        if db:
            repo = db.query(Repo).filter(Repo.id == repo_id).first()
            if repo:
                repo.status = "error"
            analysis = db.query(Analysis).filter(Analysis.repo_id == repo_id).first()
            if analysis:
                analysis.status = "error"
                analysis.error_message = str(e)
            db.commit()
        raise self.retry(exc=e, countdown=60)
    finally:
        db.close()