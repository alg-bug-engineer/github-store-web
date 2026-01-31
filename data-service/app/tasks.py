import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from celery import shared_task
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.crud.system_config import system_config as crud_system_config
from app.crud.repository import repository as crud_repo
from app.schemas.repository import RepositoryCreate, RepositoryUpdate
from app.clients.github_client import github_client
from app.sync.release_sync import sync_repository_releases
from app.models.repository import Repository as ModelRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _sync_single_repository(
    db: Session, github_item: Dict[str, Any], initial_category: Optional[str] = None
):
    """Helper to sync a single repository's details, releases, and assets."""
    repo_full_name = github_item.get("full_name")
    if not repo_full_name:
        logger.warning(f"Skipping repository with no full_name: {github_item}")
        return

    owner, name = repo_full_name.split("/")[:2]

    # Fetch full repository details from GitHub (more complete than search results)
    try:
        full_github_repo = github_client.get_repository(owner, name)
    except Exception as e:
        logger.error(f"Failed to fetch full details for {repo_full_name}: {e}")
        return

    db_repo = crud_repo.get_by_full_name(db, full_name=repo_full_name)

    github_created_at = full_github_repo.get("created_at")
    if github_created_at:
        github_created_at = datetime.fromisoformat(github_created_at.replace("Z", "+00:00"))

    github_updated_at = full_github_repo.get("updated_at")
    if github_updated_at:
        github_updated_at = datetime.fromisoformat(github_updated_at.replace("Z", "+00:00"))

    # Try to infer category if not provided or unknown, based on common terms
    inferred_category = initial_category
    if not inferred_category or inferred_category == "unknown":
        if (
            "android" in repo_full_name.lower()
            or "android" in full_github_repo.get("topics", [])
        ):
            inferred_category = "android"
        elif (
            "windows" in repo_full_name.lower()
            or "desktop" in full_github_repo.get("topics", [])
        ):
            inferred_category = "windows"
        elif (
            "macos" in repo_full_name.lower()
            or "mac" in full_github_repo.get("topics", [])
        ):
            inferred_category = "macos"
        elif (
            "linux" in repo_full_name.lower()
            or "linux" in full_github_repo.get("topics", [])
        ):
            inferred_category = "linux"
        elif (
            "cli" in repo_full_name.lower()
            or "cli" in full_github_repo.get("topics", [])
        ):
            inferred_category = "cli"
        elif (
            "web" in repo_full_name.lower()
            or "web" in full_github_repo.get("topics", [])
        ):
            inferred_category = "web"
        else:
            inferred_category = "unknown"

    repo_data = {
        "full_name": full_github_repo["full_name"],
        "owner": full_github_repo["owner"]["login"],
        "name": full_github_repo["name"],
        "description": full_github_repo.get("description"),
        "homepage": full_github_repo.get("homepage"),
        "github_id": full_github_repo["id"],
        "html_url": full_github_repo["html_url"],
        "avatar_url": full_github_repo["owner"]["avatar_url"],
        "stars": full_github_repo.get("stargazers_count", 0),
        "forks": full_github_repo.get("forks_count", 0),
        "watchers": full_github_repo.get("watchers_count", 0),
        "open_issues": full_github_repo.get("open_issues_count", 0),
        "language": full_github_repo.get("language"),
        "topics": full_github_repo.get("topics", []),
        "category": inferred_category,  # Use inferred or initial category
        "has_releases": full_github_repo.get("has_releases", False),
        "is_archived": full_github_repo.get("archived", False),
        "is_active": not full_github_repo.get("archived", False),
        "update_priority": 2,  # Default priority
        "github_created_at": github_created_at,
        "github_updated_at": github_updated_at,
        "last_synced_at": datetime.utcnow(),
    }

    if db_repo:
        repo_in = RepositoryUpdate(**repo_data)
        crud_repo.update(db, db_obj=db_repo, obj_in=repo_in, github_data=full_github_repo)
        logger.info(f"Updated repository: {repo_full_name}")
    else:
        repo_in = RepositoryCreate(**repo_data)
        db_repo = crud_repo.create(db, obj_in=repo_in, github_data=full_github_repo)
        logger.info(f"Created repository: {repo_full_name}")

    # Sync releases and assets for this repository
    if db_repo:
        try:
            sync_repository_releases(db, db_repo.id, owner, name)
            logger.info(f"Synced releases for {repo_full_name}")
        except Exception as e:
            logger.error(
                f"Failed to sync releases for {repo_full_name}: {e}", exc_info=True
            )


@shared_task
def sync_all_github_data():
    """
    Orchestrates continuous GitHub data fetching, processing, and storage.
    This task discovers new repositories and updates existing ones including their releases and assets.
    """
    logger.info("Starting comprehensive GitHub data synchronization task.")
    db = SessionLocal()
    try:
        # 1. Discover New Repositories based on system_config search filters
        search_filters_config = crud_system_config.get_by_key(
            db, key="github_search_queries"
        )
        if not search_filters_config:
            logger.warning(
                "No GitHub search queries found in system_config. Skipping new repository discovery."
            )
            # Fallback or default queries can be added here if needed
            queries = {
                "trending": "stars:>1000 sort:updated",
                "new": "created:>2023-01-01 sort:created",
            }
        else:
            queries = search_filters_config.value

        for category_name, query_str in queries.items():
            logger.info(
                f"Discovering new repositories for '{category_name}' with query: '{query_str}'"
            )
            try:
                # Fetch a few pages for discovery
                for page_num in range(1, 3):  # Fetch first 2 pages
                    search_results = github_client.search_repositories(
                        query=query_str, per_page=30, page=page_num
                    )
                    for item in search_results.get("items", []):
                        _sync_single_repository(db, item, initial_category=category_name)
            except Exception as e:
                logger.error(
                    f"Failed to discover repositories for category '{category_name}': {e}",
                    exc_info=True,
                )

        # 2. Update all existing repositories in our database
        logger.info("Updating existing repositories in the database.")
        all_db_repos: List[ModelRepository] = crud_repo.get_multi(
            db, limit=None
        )  # Fetch all repositories
        for db_repo in all_db_repos:
            try:
                # Construct a github_item dict for _sync_single_repository
                github_item = {
                    "full_name": db_repo.full_name,
                    "owner": db_repo.owner,
                    "name": db_repo.name,
                    "id": db_repo.github_id,  # Required by the helper for context
                }
                _sync_single_repository(db, github_item, initial_category=db_repo.category)
            except Exception as e:
                logger.error(
                    f"Failed to update existing repository {db_repo.full_name}: {e}",
                    exc_info=True,
                )

    finally:
        db.close()
        logger.info("Comprehensive GitHub data synchronization task finished.")
