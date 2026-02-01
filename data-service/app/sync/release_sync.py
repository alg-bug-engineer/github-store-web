"""
Release synchronization logic extracted from backend.
Handles syncing releases and assets from GitHub to the database.
"""
import os
import logging
from typing import Optional, List, Set
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.clients.github_client import github_client
from app.crud.release import release as crud_release
from app.crud.release_asset import release_asset as crud_release_asset
from app.schemas.release import ReleaseCreate, ReleaseUpdate
from app.schemas.release_asset import ReleaseAssetCreate, ReleaseAssetUpdate
from app.models.repository import Repository
from app.models.release import Release
from app.models.release_asset import ReleaseAsset

logger = logging.getLogger(__name__)


def convert_github_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    """Convert GitHub datetime string to Python datetime object."""
    if dt_str:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    return None


def extract_asset_info(asset_name: str, content_type: Optional[str] = None) -> tuple:
    """
    Extracts platform and file type from an asset name and content type.
    Returns (platform, file_type) tuple.
    """
    platform = None
    file_type = None

    name_lower = asset_name.lower()
    _, ext = os.path.splitext(name_lower)

    # Determine File Type
    if ext == ".apk":
        file_type = "apk"
    elif ext == ".exe":
        file_type = "executable"
    elif ext == ".dmg":
        file_type = "disk_image"
    elif ext in [".deb", ".rpm"]:
        file_type = "package"
    elif ext == ".zip" or ("zip" in content_type if content_type else False):
        file_type = "archive"
    elif ext == ".tar.gz" or ext == ".tgz":
        file_type = "archive"
    elif ext == ".appimage":
        file_type = "appimage"
    elif ext == ".msi":
        file_type = "installer"
    elif "text" in content_type if content_type else False:
        file_type = "text"
    elif "image" in content_type if content_type else False:
        file_type = "image"
    else:
        file_type = ext.lstrip(".") if ext else None

    # Determine Platform
    if "android" in name_lower or file_type == "apk":
        platform = "android"
    elif "windows" in name_lower or file_type == "executable" or file_type == "installer":
        platform = "windows"
    elif "macos" in name_lower or "darwin" in name_lower or file_type == "disk_image":
        platform = "macos"
    elif "linux" in name_lower or file_type == "appimage" or file_type == "package":
        platform = "linux"
    elif "web" in name_lower:
        platform = "web"
    elif "all" in name_lower or "universal" in name_lower:
        platform = "universal"

    return platform, file_type


def sync_repository_releases(db: Session, repo_id: int, owner: str, repo_name: str):
    """
    Synchronize releases and assets for a given repository from GitHub.
    """
    try:
        github_releases = github_client.list_releases(owner, repo_name)
        for gh_release in github_releases:
            release_data = {
                "repo_id": repo_id,
                "github_release_id": gh_release["id"],
                "tag_name": gh_release["tag_name"],
                "name": gh_release.get("name"),
                "body": gh_release.get("body"),
                "is_prerelease": gh_release["prerelease"],
                "is_draft": gh_release["draft"],
                "is_latest": gh_release.get("tag_name") == gh_release.get("target_commitish"),
                "published_at": convert_github_datetime(gh_release.get("published_at")),
            }
            db_release = crud_release.get_by_github_release_id(
                db, github_release_id=gh_release["id"]
            )
            if db_release:
                release_in = ReleaseUpdate(**release_data)
                crud_release.update(db, db_obj=db_release, obj_in=release_in)
            else:
                release_in = ReleaseCreate(**release_data)
                db_release = crud_release.create(db, obj_in=release_in)

            # Sync assets for this release
            for gh_asset in gh_release.get("assets", []):
                asset_platform, asset_file_type = extract_asset_info(
                    gh_asset["name"], gh_asset.get("content_type")
                )

                asset_data = {
                    "release_id": db_release.id,
                    "github_asset_id": gh_asset["id"],
                    "name": gh_asset["name"],
                    "label": gh_asset.get("label"),
                    "content_type": gh_asset["content_type"],
                    "size": gh_asset["size"],
                    "browser_download_url": gh_asset["browser_download_url"],
                    "download_count": gh_asset["download_count"],
                    "platform": asset_platform,
                    "file_type": asset_file_type,
                }
                db_asset = crud_release_asset.get_by_github_asset_id(
                    db, github_asset_id=gh_asset["id"]
                )
                if db_asset:
                    asset_in = ReleaseAssetUpdate(**asset_data)
                    crud_release_asset.update(db, db_obj=db_asset, obj_in=asset_in)
                else:
                    asset_in = ReleaseAssetCreate(**asset_data)
                    crud_release_asset.create(db, obj_in=asset_in)
        # After syncing releases, update repository metadata
        update_repository_release_metadata(db, repo_id)

    except Exception as e:
        logger.error(f"Error syncing releases for {owner}/{repo_name}: {e}")


def update_repository_release_metadata(db: Session, repo_id: int):
    """
    Update repository's has_releases, detected_platforms, total_downloads,
    latest_version, and latest_release_date based on actual release data.
    """
    try:
        repo = db.query(Repository).filter(Repository.id == repo_id).first()
        if not repo:
            return

        # Check if repository has any releases
        releases_count = db.query(Release).filter(Release.repo_id == repo_id).count()
        has_releases = releases_count > 0

        # Get latest release info
        latest_release = (
            db.query(Release)
            .filter(Release.repo_id == repo_id, Release.is_draft == False)
            .order_by(Release.published_at.desc())
            .first()
        )

        latest_version = None
        latest_release_date = None
        if latest_release:
            latest_version = latest_release.tag_name
            latest_release_date = latest_release.published_at

        # Get all distinct platforms from release assets
        platforms_query = (
            db.query(ReleaseAsset.platform)
            .join(Release, Release.id == ReleaseAsset.release_id)
            .filter(Release.repo_id == repo_id)
            .filter(ReleaseAsset.platform.isnot(None))
            .distinct()
        )
        platforms: Set[str] = {row[0] for row in platforms_query.all() if row[0]}

        # Normalize platform names for consistency
        normalized_platforms: List[str] = []
        platform_map = {
            'macos': 'mac',
            'darwin': 'mac',
            'win32': 'windows',
            'win64': 'windows',
        }
        for p in platforms:
            normalized = platform_map.get(p.lower(), p.lower())
            if normalized not in normalized_platforms:
                normalized_platforms.append(normalized)

        # Calculate total downloads from all assets
        total_downloads = (
            db.query(func.sum(ReleaseAsset.download_count))
            .join(Release, Release.id == ReleaseAsset.release_id)
            .filter(Release.repo_id == repo_id)
            .scalar()
        ) or 0

        # Update repository
        repo.has_releases = has_releases
        repo.detected_platforms = normalized_platforms if normalized_platforms else []
        repo.total_downloads = total_downloads
        repo.latest_version = latest_version
        repo.latest_release_date = latest_release_date

        db.add(repo)
        db.commit()

        logger.info(
            f"Updated repo {repo.full_name}: has_releases={has_releases}, "
            f"platforms={normalized_platforms}, downloads={total_downloads}, "
            f"latest={latest_version}"
        )

    except Exception as e:
        logger.error(f"Error updating repository metadata for repo_id={repo_id}: {e}")
        db.rollback()
