from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
from app.api import deps
from app.models.repository import Repository
from app.models.release import Release
from app.models.release_asset import ReleaseAsset


router = APIRouter()

@router.get("/overview", response_model=dict)
def get_stats_overview(
    db: Session = Depends(deps.get_db)
):
    """
    Get an overview of statistics for repositories, releases, downloads, and categories.
    """
    repositories_count = db.query(Repository).filter(Repository.is_active == True).count()
    releases_count = db.query(Release).count()
    total_downloads = db.query(func.sum(Repository.total_downloads)).scalar()
    categories_count = db.query(Repository.primary_category).filter(Repository.primary_category.isnot(None)).distinct().count()

    return {
        "repositories_count": repositories_count,
        "releases_count": releases_count,
        "total_downloads": total_downloads if total_downloads is not None else 0,
        "categories_count": categories_count
    }


@router.get("/detailed", response_model=dict)
def get_detailed_stats(
    db: Session = Depends(deps.get_db)
):
    """
    Get detailed statistics including platform breakdown and view mode counts.
    """
    # Total counts
    total_repos = db.query(Repository).filter(Repository.is_active == True).count()
    apps_count = db.query(Repository).filter(
        Repository.is_active == True,
        Repository.has_releases == True
    ).count()

    # Releases and downloads
    releases_count = db.query(Release).count()
    total_downloads = db.query(func.sum(Repository.total_downloads)).scalar() or 0

    # Platform counts (repos that have assets for each platform)
    platform_stats = {}
    platforms = ['windows', 'macos', 'linux', 'android']

    for platform in platforms:
        # Count repos that have this platform in detected_platforms array
        count = db.query(Repository).filter(
            Repository.is_active == True,
            Repository.detected_platforms.contains([platform])
        ).count()
        platform_stats[platform] = count

    # Category breakdown
    category_counts = (
        db.query(Repository.primary_category, func.count(Repository.id))
        .filter(Repository.is_active == True, Repository.primary_category.isnot(None))
        .group_by(Repository.primary_category)
        .all()
    )
    categories = {cat: count for cat, count in category_counts if cat}

    # Language stats (top 10)
    language_counts = (
        db.query(Repository.language, func.count(Repository.id))
        .filter(Repository.is_active == True, Repository.language.isnot(None))
        .group_by(Repository.language)
        .order_by(func.count(Repository.id).desc())
        .limit(10)
        .all()
    )
    languages = {lang: count for lang, count in language_counts if lang}

    # Stars stats
    total_stars = db.query(func.sum(Repository.stars)).scalar() or 0
    avg_stars = db.query(func.avg(Repository.stars)).scalar() or 0

    return {
        "total": {
            "repositories": total_repos,
            "apps": apps_count,
            "all": total_repos,
            "releases": releases_count,
            "downloads": total_downloads,
            "stars": total_stars,
            "avg_stars": round(avg_stars, 1)
        },
        "platforms": platform_stats,
        "categories": categories,
        "languages": languages
    }


@router.get("/categories", response_model=dict)
def get_categories_list(
    db: Session = Depends(deps.get_db)
):
    """
    Get a list of all detected categories with their counts.
    """
    category_counts = (
        db.query(Repository.primary_category, func.count(Repository.id))
        .filter(Repository.primary_category.isnot(None))
        .group_by(Repository.primary_category)
        .all()
    )

    categories_data = []
    
    DISPLAY_NAMES = {
        'productivity': 'Productivity',
        'developer_tools': 'Developer Tools',
        'media': 'Media & Entertainment',
        'utilities': 'Utilities',
        'games': 'Games',
        'security': 'Security',
        'education': 'Education',
        'other': 'Other' # Assuming 'other' category
    }

    for category_id, count in category_counts:
        display_name = DISPLAY_NAMES.get(category_id, category_id.replace('_', ' ').title())
        categories_data.append({
            "id": category_id,
            "name": display_name,
            "count": count
        })
    
    # Sort categories alphabetically by name
    categories_data.sort(key=lambda x: x['name'])

    return {"categories": categories_data}
