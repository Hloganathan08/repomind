import anthropic
import json
import re
from app.core.config import settings

client = anthropic.Anthropic(api_key=settings.anthropic_api_key)


async def summarize_file(path: str, content: str) -> str:
    truncated = content[:3000]
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": f"""Summarize this file in 2-3 sentences. Focus on: what it does, key functions/classes, and its role in the codebase.

File: {path}
```
{truncated}
```

Respond with only the summary, no preamble."""
        }]
    )
    return message.content[0].text


async def analyze_architecture(repo_name: str, file_summaries: list) -> dict:
    files_text = "\n".join([f"- {f['path']}: {f['summary']}" for f in file_summaries[:30]])

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1500,
        messages=[{
            "role": "user",
            "content": f"""Analyze this codebase and provide a structured response as JSON.

Repository: {repo_name}
Files analyzed:
{files_text}

Respond with ONLY valid JSON, no markdown fences, no preamble:
{{
  "architecture_summary": "2-3 sentence overview of the architecture",
  "tech_stack": ["technology1", "technology2"],
  "entry_points": ["path/to/main.py", "path/to/index.ts"],
  "onboarding_guide": "A paragraph explaining how a new developer should approach this codebase"
}}"""
        }]
    )

    text = message.content[0].text.strip()
    text = re.sub(r'^```(?:json)?\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    text = text.strip()

    try:
        return json.loads(text)
    except Exception:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
        return {
            "architecture_summary": text,
            "tech_stack": [],
            "entry_points": [],
            "onboarding_guide": ""
        }