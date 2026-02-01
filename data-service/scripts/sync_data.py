#!/usr/bin/env python3
"""
Manual data sync script for GitHub Releases Store.
Run this script to sync repositories, releases, and assets from GitHub.

Usage:
    python scripts/sync_data.py              # Full sync
    python scripts/sync_data.py --repos-only # Only sync repositories
    python scripts/sync_data.py --limit 10   # Limit number of repos per category
"""

import argparse
import logging
import sys
import os
from datetime import datetime
from typing import Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.db.session import SessionLocal
from app.clients.github_client import github_client
from app.crud.repository import repository as crud_repo
from app.crud.release import release as crud_release
from app.crud.release_asset import release_asset as crud_asset
from app.crud.system_config import system_config
from app.schemas.repository import RepositoryCreate, RepositoryUpdate
from app.schemas.release import ReleaseCreate, ReleaseUpdate
from app.schemas.release_asset import ReleaseAssetCreate, ReleaseAssetUpdate
from app.services.category_service import get_category_service, detect_category

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Popular repositories to sync (pre-defined list for initial data)
POPULAR_REPOS = [
    # Android Apps
    "AntennaPod/AntennaPod",
    "ankidroid/Anki-Android",
    "breezy-weather/breezy-weather",
    # Desktop Apps
    "obsproject/obs-studio",
    "bitwarden/clients",
    # CLI Tools
    "BurntSushi/ripgrep",
    "cli/cli",
    "neovim/neovim",
]


def parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    """Parse GitHub datetime string to datetime object."""
    if not dt_str:
        return None
    return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))


def detect_platform(filename: str) -> Optional[str]:
    """Detect platform from filename."""
    filename_lower = filename.lower()
    if any(x in filename_lower for x in [".apk", "android"]):
        return "android"
    elif any(x in filename_lower for x in [".exe", ".msi", "windows", "win32", "win64"]):
        return "windows"
    elif any(x in filename_lower for x in [".dmg", ".pkg", "macos", "darwin", "mac"]):
        return "macos"
    elif any(x in filename_lower for x in [".deb", ".rpm", ".appimage", "linux"]):
        return "linux"
    return None


def detect_file_type(filename: str) -> Optional[str]:
    """Detect file type from filename."""
    filename_lower = filename.lower()
    if filename_lower.endswith(".apk"):
        return "apk"
    elif filename_lower.endswith(".exe"):
        return "exe"
    elif filename_lower.endswith(".msi"):
        return "msi"
    elif filename_lower.endswith(".dmg"):
        return "dmg"
    elif filename_lower.endswith(".pkg"):
        return "pkg"
    elif filename_lower.endswith(".deb"):
        return "deb"
    elif filename_lower.endswith(".rpm"):
        return "rpm"
    elif filename_lower.endswith(".appimage"):
        return "appimage"
    elif filename_lower.endswith(".tar.gz") or filename_lower.endswith(".tgz"):
        return "tar.gz"
    elif filename_lower.endswith(".zip"):
        return "zip"
    return None


def log_category_config():
    """Log loaded category configuration."""
    service = get_category_service()
    categories = service.get_category_ids()
    logger.info(f"Loaded categories: {categories}")


def sync_repository(db, owner: str, repo: str) -> Optional[int]:
    """Sync a single repository from GitHub."""
    try:
        repo_data = github_client.get_repository(owner, repo)
        full_name = repo_data["full_name"]

        db_repo = crud_repo.get_by_full_name(db, full_name=full_name)

        repo_dict = {
            "full_name": full_name,
            "owner": repo_data["owner"]["login"],
            "name": repo_data["name"],
            "description": repo_data.get("description"),
            "homepage": repo_data.get("homepage"),
            "github_id": repo_data["id"],
            "html_url": repo_data["html_url"],
            "avatar_url": repo_data["owner"]["avatar_url"],
            "stars": repo_data.get("stargazers_count", 0),
            "forks": repo_data.get("forks_count", 0),
            "watchers": repo_data.get("watchers_count", 0),
            "open_issues": repo_data.get("open_issues_count", 0),
            "language": repo_data.get("language"),
            "topics": repo_data.get("topics", []),
            "category": detect_category(repo_data),
            "has_releases": True,  # We'll update this after checking releases
            "is_archived": repo_data.get("archived", False),
            "is_active": not repo_data.get("archived", False),
            "update_priority": 2,
            "github_created_at": parse_datetime(repo_data.get("created_at")),
            "github_updated_at": parse_datetime(repo_data.get("updated_at")),
            "last_synced_at": datetime.utcnow(),
        }

        if db_repo:
            crud_repo.update(db, db_obj=db_repo, obj_in=RepositoryUpdate(**repo_dict), github_data=repo_data)
            logger.info(f"Updated repository: {full_name}")
            return db_repo.id
        else:
            new_repo = crud_repo.create(db, obj_in=RepositoryCreate(**repo_dict), github_data=repo_data)
            logger.info(f"Created repository: {full_name}")
            return new_repo.id

    except Exception as e:
        logger.error(f"Failed to sync repository {owner}/{repo}: {e}")
        return None


def sync_releases(db, repo_id: int, owner: str, repo: str, limit: int = 5):
    """Sync releases for a repository."""
    try:
        all_releases = github_client.list_releases(owner, repo)
        releases = all_releases[:limit]

        if not releases:
            # Update has_releases to False
            db_repo = crud_repo.get(db, id=repo_id)
            if db_repo:
                crud_repo.update(db, db_obj=db_repo, obj_in=RepositoryUpdate(
                    has_releases=False,
                    full_name=db_repo.full_name,
                    owner=db_repo.owner,
                    name=db_repo.name,
                ), github_data={})
            return

        for idx, release_data in enumerate(releases):
            release_dict = {
                "repo_id": repo_id,
                "github_release_id": release_data["id"],
                "tag_name": release_data["tag_name"],
                "name": release_data.get("name"),
                "body": release_data.get("body"),
                "is_prerelease": release_data.get("prerelease", False),
                "is_draft": release_data.get("draft", False),
                "is_latest": idx == 0,  # First release is latest
                "published_at": parse_datetime(release_data.get("published_at")),
            }

            db_release = crud_release.get_by_github_release_id(
                db, github_release_id=release_data["id"]
            )

            if db_release:
                crud_release.update(db, db_obj=db_release, obj_in=ReleaseUpdate(**release_dict))
                release_id = db_release.id
            else:
                new_release = crud_release.create(db, obj_in=ReleaseCreate(**release_dict))
                release_id = new_release.id

            # Sync assets for this release
            sync_assets(db, release_id, release_data.get("assets", []))

        logger.info(f"Synced {len(releases)} releases for {owner}/{repo}")

    except Exception as e:
        logger.error(f"Failed to sync releases for {owner}/{repo}: {e}")


def sync_assets(db, release_id: int, assets: list):
    """Sync assets for a release."""
    for asset_data in assets:
        filename = asset_data["name"]

        asset_dict = {
            "release_id": release_id,
            "github_asset_id": asset_data["id"],
            "name": filename,
            "label": asset_data.get("label"),
            "content_type": asset_data.get("content_type"),
            "size": asset_data.get("size"),
            "browser_download_url": asset_data["browser_download_url"],
            "download_count": asset_data.get("download_count", 0),
            "platform": detect_platform(filename),
            "file_type": detect_file_type(filename),
        }

        db_asset = crud_asset.get_by_github_asset_id(
            db, github_asset_id=asset_data["id"]
        )

        if db_asset:
            crud_asset.update(db, db_obj=db_asset, obj_in=ReleaseAssetUpdate(**asset_dict))
        else:
            crud_asset.create(db, obj_in=ReleaseAssetCreate(**asset_dict))


def sync_from_search(db, limit_per_category: int = 30):
    """Sync repositories from search filters in system_config."""
    search_filters_config = system_config.get_by_key(db, key="search_filters")
    if not search_filters_config:
        logger.warning("No search filters found in system_config.")
        return

    filters = search_filters_config.value
    for category, query in filters.items():
        logger.info(f"Searching category '{category}' with query: {query}")
        try:
            search_results = github_client.search_repositories(
                query=query, per_page=limit_per_category
            )
            for item in search_results.get("items", []):
                owner = item["owner"]["login"]
                repo_name = item["name"]
                repo_id = sync_repository(db, owner, repo_name)
                if repo_id:
                    sync_releases(db, repo_id, owner, repo_name)
        except Exception as e:
            logger.error(f"Failed to search category '{category}': {e}")


def sync_popular_repos(db, repos_only: bool = False):
    """Sync pre-defined popular repositories."""
    for full_name in POPULAR_REPOS:
        parts = full_name.split("/")
        if len(parts) != 2:
            continue
        owner, repo = parts

        repo_id = sync_repository(db, owner, repo)
        if repo_id and not repos_only:
            sync_releases(db, repo_id, owner, repo)


def main():
    parser = argparse.ArgumentParser(description="Sync GitHub data")
    parser.add_argument("--repos-only", action="store_true", help="Only sync repositories, not releases")
    parser.add_argument("--limit", type=int, default=30, help="Limit repos per category")
    parser.add_argument("--popular-only", action="store_true", help="Only sync pre-defined popular repos")
    args = parser.parse_args()

    logger.info("Starting data sync...")
    log_category_config()
    db = SessionLocal()

    try:
        # Sync pre-defined popular repos
        logger.info("Syncing popular repositories...")
        sync_popular_repos(db, repos_only=args.repos_only)

        # if not args.popular_only:
        # Sync from search filters
        logger.info("Syncing from search filters...")
        sync_from_search(db, limit_per_category=args.limit)

        logger.info("Data sync completed successfully!")

        # Print summary
        repo_count = db.query(crud_repo.model).count()
        release_count = db.query(crud_release.model).count()
        asset_count = db.query(crud_asset.model).count()

        logger.info(f"Summary: {repo_count} repositories, {release_count} releases, {asset_count} assets")

    except Exception as e:
        logger.error(f"Sync failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
