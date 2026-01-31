from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func # Import func
from app.api import deps
from app.models.repository import Repository
from app.models.release import Release
from app.models.release_asset import ReleaseAsset
from app.utils.category_detector import CATEGORY_KEYWORDS # Import CATEGORY_KEYWORDS


router = APIRouter()

@router.get("/overview", response_model=dict)
def get_stats_overview(
    db: Session = Depends(deps.get_db)
):
    """
    Get an overview of statistics for repositories, releases, downloads, and categories.
    """
    repositories_count = db.query(Repository).count()
    releases_count = db.query(Release).count()
    # Sum of total_downloads from all repositories
    total_downloads = db.query(func.sum(Repository.total_downloads)).scalar()
    categories_count = db.query(Repository.primary_category).filter(Repository.primary_category.isnot(None)).distinct().count()

    return {
        "repositories_count": repositories_count,
        "releases_count": releases_count,
        "total_downloads": total_downloads if total_downloads is not None else 0,
        "categories_count": categories_count
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
