import base64
import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.api import deps
from app.clients.github_client import github_client
from app.clients.kimi_client import kimi_client
from app.schemas.readme_cache import ReadmeCacheCreate

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/repositories/{repo_id}/summarize", response_model=Dict[str, str])
async def summarize_repository(
    repo_id: int,
    db: Session = Depends(deps.get_db),
    # current_user: models.User = Depends(deps.get_current_active_user), # Optional: Add if auth is needed
) -> Any:
    """
    Generates a user-friendly summary of a repository's README using an AI model.
    """
    repo = crud.repository.get(db, id=repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    readme_text = ""
    # 1. Try to get README from cache
    cached_readme = crud.readme_cache.get_by_repo_id(db, repo_id=repo.id)
    if cached_readme and cached_readme.content:
        readme_text = cached_readme.content
        logger.info(f"Using cached README for {repo.full_name}")
    else:
        # 2. If not in cache, fetch from GitHub
        logger.info(f"Fetching README from GitHub for {repo.full_name}")
        try:
            readme_data = github_client.get_readme(repo.owner, repo.name)
            if readme_data.get("encoding") == "base64":
                readme_text = base64.b64decode(readme_data["content"]).decode("utf-8")
                # Save to cache for future use
                readme_in = ReadmeCacheCreate(
                    repo_id=repo.id,
                    content=readme_text,
                    encoding=readme_data["encoding"],
                )
                crud.readme_cache.create(db, obj_in=readme_in)
                logger.info(f"Cached new README for {repo.full_name}")
            else:
                readme_text = readme_data.get("content", "")

        except Exception as e:
            logger.error(f"Failed to fetch or process README for {repo.full_name}: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve README from GitHub.")

    if not readme_text:
        raise HTTPException(status_code=404, detail="README content is empty or not found.")

    # 3. Generate summary with AI
    logger.info(f"Generating AI summary for {repo.full_name}")
    try:
        # Truncate README to fit model context window (e.g., 6000 tokens for 8k model)
        truncated_readme = readme_text[:20000] 

        prompt = f"""请帮我将以下 README 内容总结成一段150字左右的、面向普通用户的应用介绍。请用友好、通俗的语言，提取这个应用的核心功能和主要使用场景。请直接返回总结内容，不要包含任何额外说明或标题。

README内容如下：
---
{truncated_readme}
"""
        context_for_ai = f"项目名称: {repo.full_name}\n项目描述: {repo.description}"

        ai_response = await kimi_client.chat(user_message=prompt, context=context_for_ai)
        
        summary = ai_response["choices"][0]["message"]["content"]
        return {"summary": summary}

    except Exception as e:
        logger.error(f"AI summary generation failed for {repo.full_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate summary from AI model.")