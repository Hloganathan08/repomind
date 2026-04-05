import httpx
from typing import Optional


async def fetch_repo_info(full_name: str, token: Optional[str] = None) -> dict:
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(
            f"https://api.github.com/repos/{full_name}",
            headers=headers,
        )

    if response.status_code != 200:
        return None

    data = response.json()
    return {
        "github_repo_id": str(data["id"]),
        "full_name": data["full_name"],
        "owner": data["owner"]["login"],
        "name": data["name"],
        "description": data.get("description"),
        "language": data.get("language"),
        "stars": data.get("stargazers_count", 0),
        "is_private": data.get("private", False),
        "default_branch": data.get("default_branch", "main"),
    }


async def fetch_repo_tree(full_name: str, branch: str = "main", token: Optional[str] = None) -> list:
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(
            f"https://api.github.com/repos/{full_name}/git/trees/{branch}?recursive=1",
            headers=headers,
        )

    if response.status_code != 200:
        return []

    data = response.json()
    return [f for f in data.get("tree", []) if f.get("type") == "blob"]


async def fetch_file_content(full_name: str, path: str, branch: str = "main", token: Optional[str] = None) -> Optional[str]:
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(
            f"https://api.github.com/repos/{full_name}/contents/{path}?ref={branch}",
            headers=headers,
        )

    if response.status_code != 200:
        return None

    data = response.json()
    if data.get("encoding") == "base64":
        import base64
        return base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
    return None