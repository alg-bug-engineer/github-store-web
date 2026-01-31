from typing import Any, List, Optional, Dict
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, func

from app import crud
from app.api import deps
from app.models.repository import Repository as DBRepository
from app.crud.release import release as crud_release
from app.crud.release_asset import release_asset as crud_release_asset
from app.schemas.release_asset import ReleaseAsset
from app.schemas.repository import Repository, Topic
from app.schemas.release import Release
from app.models.user import User

logger = logging.getLogger(__name__)


router = APIRouter()


# Note: sync_repository_releases has been moved to data-service
# This API now only handles read-only queries


@router.get("/topics/", response_model=List[Topic])
def get_popular_topics(
    db: Session = Depends(deps.get_db),
    limit: int = Query(50, ge=10, le=200, description="Limit the number of topics returned"),
) -> Any:
    """
    Get a list of the most popular topics (tags) across all repositories,
    ranked by occurrence.
    """
    # The result from query.all() is a list of KeyedTuples (like named tuples).
    # Pydantic's `from_attributes=True` can automatically convert them to `Topic` schemas
    # because the column labels ('topic', 'count') match the schema field names.
    topics = crud.repository.get_all_topics(db, limit=limit)
    return topics


@router.get("/")
async def search_repositories(
    db: Session = Depends(deps.get_db),
    view: str = Query("apps", description="Filter by view type: 'apps' (has releases) or 'all'"),
    platform: Optional[str] = Query(None, description="Filter by platform (e.g., windows, mac, linux, android)"),
    category: Optional[str] = Query(None, description="Filter by primary category"),
    topics: Optional[str] = Query(None, description="Filter by topics (comma-separated)"),
    language: Optional[str] = Query(None, description="Filter by programming language"),
    q: str = Query("", description="Search query string"),
    sort: str = Query("stars", description="Sort by: stars, updated, created, downloads"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: Optional[User] = Depends(deps.get_current_active_user_or_none),
) -> Dict[str, Any]:
    """
    Search repositories. Returns paginated results with total count.
    Searches the local database only.
    """
    def parse_csv(value: Optional[str]) -> List[str]:
        if not value:
            return []
        return [item.strip() for item in value.split(",") if item.strip()]

    platforms = parse_csv(platform)
    categories = parse_csv(category)
    topics_list = parse_csv(topics)
    languages = parse_csv(language)

    logger.info(
        f"Search request: q={q}, platform={platforms}, category={categories}, topics={topics_list}, language={languages}, sort={sort}"
    )

    # Build base query
    query_builder = db.query(DBRepository).filter(DBRepository.is_active == True)

    # Apply view filter
    if view == "apps":
        query_builder = query_builder.filter(DBRepository.has_releases == True)

    # Apply text search if query provided
    if q:
        search_term = f"%{q.lower()}%"
        query_builder = query_builder.filter(
            or_(
                func.lower(DBRepository.name).like(search_term),
                func.lower(DBRepository.full_name).like(search_term),
                func.lower(DBRepository.description).like(search_term),
                # Search in topics array
                DBRepository.topics.contains([q.lower()])
            )
        )

    # Apply platform filter
    if platforms:
        query_builder = query_builder.filter(DBRepository.detected_platforms.overlap(platforms))

    # Apply category filter (matches primary_category or legacy category)
    if categories:
        query_builder = query_builder.filter(
            or_(
                DBRepository.primary_category.in_(categories),
                DBRepository.category.in_(categories),
            )
        )
    
    # Apply topics filter
    if topics_list:
        query_builder = query_builder.filter(DBRepository.topics.overlap(topics_list))

    # Apply language filter
    if languages:
        query_builder = query_builder.filter(DBRepository.language.in_(languages))

    # Get total count before pagination
    total = query_builder.count()

    # Apply sorting
    if sort == "stars":
        query_builder = query_builder.order_by(desc(DBRepository.stars))
    elif sort == "updated":
        query_builder = query_builder.order_by(desc(DBRepository.github_updated_at))
    elif sort == "created":
        query_builder = query_builder.order_by(desc(DBRepository.github_created_at))
    elif sort == "downloads":
        query_builder = query_builder.order_by(desc(DBRepository.total_downloads))
    else:
        query_builder = query_builder.order_by(desc(DBRepository.stars))


    # Apply pagination
    repositories = query_builder.offset((page - 1) * per_page).limit(per_page).all()

    logger.info(f"Found {len(repositories)} repositories (total: {total})")

    # Add is_favorited flag
    repos_with_fav_status = []
    for repo in repositories:
        is_favorited = False
        if current_user:
            favorite = crud.user_favorite.get_by_user_id_and_repo_id(db, user_id=current_user.id, repo_id=repo.id)
            is_favorited = favorite is not None
        repo_data = Repository.model_validate(repo)
        repo_data.is_favorited = is_favorited
        repos_with_fav_status.append(repo_data)

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "items": repos_with_fav_status
    }


@router.get("/{owner}/{repo}")
async def get_repository(
    owner: str,
    repo: str,
    db: Session = Depends(deps.get_db),
    current_user: Optional[User] = Depends(deps.get_current_active_user_or_none),
) -> Dict[str, Any]:
    """
    Get repository details by owner and repository name.
    Includes releases and latest release info.
    """
    logger.info(f"Getting repository: {owner}/{repo}")

    full_name = f"{owner}/{repo}"
    repository = crud.repository.get_by_full_name(db, full_name=full_name)

    if not repository:
        raise HTTPException(status_code=404, detail=f"Repository {owner}/{repo} not found in store.")

    # Add is_favorited flag
    is_favorited = False
    if current_user and repository:
        favorite = crud.user_favorite.get_by_user_id_and_repo_id(db, user_id=current_user.id, repo_id=repository.id)
        is_favorited = favorite is not None
    
    repository_data = Repository.model_validate(repository)
    repository_data.is_favorited = is_favorited

    # Get releases for this repository
    releases = crud_release.get_multi_by_repo_id(db, repo_id=repository.id, limit=10)

    # Get latest release
    latest_release = crud_release.get_latest_release_by_repo_id(db, repo_id=repository.id)

    # Get assets for latest release
    latest_assets = []
    if latest_release:
        latest_assets = crud_release_asset.get_multi_by_release_id(db, release_id=latest_release.id)

    return {
        "repository": repository_data,
        "releases": [Release.model_validate(r) for r in releases],
        "latest_release": Release.model_validate(latest_release) if latest_release else None,
        "latest_assets": [ReleaseAsset.model_validate(a) for a in latest_assets]
    }


@router.get("/{owner}/{repo}/releases", response_model=List[Release])
def list_releases(
    owner: str,
    repo: str,
    db: Session = Depends(deps.get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
) -> Any:
    """
    List releases for a repository.
    """
    repository = crud.repository.get_by_full_name(db, full_name=f"{owner}/{repo}")
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")

    releases = crud_release.get_multi_by_repo_id(
        db, repo_id=repository.id, skip=(page - 1) * per_page, limit=per_page
    )
    return releases


@router.get("/releases/{release_id}/assets", response_model=List[ReleaseAsset])
def list_release_assets(
    release_id: int,
    db: Session = Depends(deps.get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
) -> Any:
    """
    List assets for a specific release.
    """
    release = crud_release.get(db, id=release_id)
    if not release:
        raise HTTPException(status_code=404, detail="Release not found")

    assets = crud_release_asset.get_multi_by_release_id(
        db, release_id=release.id, skip=(page - 1) * per_page, limit=per_page
    )
    return assets
